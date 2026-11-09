#!/usr/bin/env python3
"""Generate a synthetic "Yammer" dataset for the SQL analytics cases.

The data is fake. It has the same tables and columns as the Yammer case
studies in the Mode / ThoughtSpot SQL tutorial, and it is built so that the
case questions lead to the same conclusions:

1. Drop in engagement: weekly engaged users fall in August 2014. Growth is
   normal. The drop comes from users older than ~10 weeks, from phones (and
   a bit from tablets), and from weekly digest email clickthroughs.
2. Search: autocomplete is used in ~25% of sessions, full search in ~8%.
   Full searches come in bursts, almost never lead to clicks, clicks are
   spread evenly over positions 1-10, and users rarely search again in the
   next month. Autocomplete users keep using it.
3. A/B test "publisher_update" (June 2014): the test group posts ~50% more
   messages, logs in more and is engaged on more days. But all new users
   were put in the control group. Without new users the lift is smaller,
   but still strong.

Usage: python3 generate_yammer.py OUTPUT_DIR

Only the standard library is used. The random seed is fixed, so the output
is the same on every run.
"""

import csv
import math
import os
import random
import sys
from datetime import date, datetime, timedelta

SEED = 20140902

USERS_START = date(2013, 1, 1)
USERS_END = date(2014, 8, 31)  # inclusive
EVENTS_START = date(2014, 5, 1)
EVENTS_END = date(2014, 8, 31)  # inclusive
END_TS = datetime(2014, 9, 1)  # exclusive upper bound for all timestamps

AB_START = date(2014, 6, 1)
AB_END = date(2014, 7, 1)  # exclusive
DROP_START = date(2014, 8, 1)

# ---------------------------------------------------------------------------
# Value sets
# ---------------------------------------------------------------------------

LANGUAGES = [
    ("english", 55), ("spanish", 8), ("japanese", 5), ("german", 5),
    ("french", 5), ("russian", 4), ("korean", 3), ("italian", 3),
    ("chinese", 3), ("portugese", 3), ("arabic", 2), ("indian", 2),
    ("turkish", 2),
]

COUNTRIES_BY_LANGUAGE = {
    "english": [("United States", 55), ("United Kingdom", 12), ("Canada", 8),
                ("Australia", 6), ("India", 5), ("Ireland", 2),
                ("Singapore", 2), ("South Africa", 2), ("Nigeria", 2),
                ("Netherlands", 2), ("Sweden", 1), ("Norway", 1),
                ("Denmark", 1), ("Finland", 1)],
    "spanish": [("Mexico", 30), ("Spain", 30), ("Colombia", 12),
                ("Argentina", 12), ("Chile", 8), ("Venezuela", 8)],
    "japanese": [("Japan", 100)],
    "german": [("Germany", 75), ("Austria", 12), ("Switzerland", 13)],
    "french": [("France", 80), ("Belgium", 12), ("Switzerland", 8)],
    "russian": [("Russia", 100)],
    "korean": [("Korea", 100)],
    "italian": [("Italy", 100)],
    "chinese": [("China", 55), ("Taiwan", 25), ("Hong Kong", 20)],
    "portugese": [("Brazil", 80), ("Portugal", 20)],
    "arabic": [("Saudi Arabia", 40), ("United Arab Emirates", 30),
               ("Egypt", 30)],
    "indian": [("India", 100)],
    "turkish": [("Turkey", 100)],
}
ALL_COUNTRIES = sorted({c for v in COUNTRIES_BY_LANGUAGE.values() for c, _ in v})

COMPUTERS = ["dell inspiron notebook", "macbook pro", "lenovo thinkpad",
             "macbook air", "acer aspire notebook", "asus chromebook",
             "hp pavilion desktop", "dell inspiron desktop",
             "acer aspire desktop", "mac mini", "windows surface"]
PHONES = ["iphone 5", "iphone 5s", "iphone 4s", "samsung galaxy s4",
          "nexus 5", "htc one", "nokia lumia 635", "samsung galaxy note",
          "amazon fire phone"]
TABLETS = ["ipad air", "ipad mini", "nexus 7", "nexus 10", "kindle fire",
           "samsung galaxy tablet"]
DEVICE_CLASS = {}
for _d in COMPUTERS:
    DEVICE_CLASS[_d] = "computer"
for _d in PHONES:
    DEVICE_CLASS[_d] = "phone"
for _d in TABLETS:
    DEVICE_CLASS[_d] = "tablet"

# Session-start hour weights (work hours are busier).
HOUR_WEIGHTS = [1, 1, 1, 1, 1, 2, 4, 8, 12, 14, 14, 12, 10, 12, 13, 13, 11,
                8, 6, 5, 4, 3, 2, 1]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def fmt(ts):
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def daterange(start, end_inclusive):
    d = start
    while d <= end_inclusive:
        yield d
        d += timedelta(days=1)


def poisson(rng, lam):
    """Knuth's method; lam is small here."""
    if lam <= 0:
        return 0
    if lam > 30:
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    l_ = math.exp(-lam)
    k, p = 0, 1.0
    while True:
        p *= rng.random()
        if p <= l_:
            return k
        k += 1


def weighted(rng, pairs):
    total = sum(w for _, w in pairs)
    x = rng.random() * total
    for v, w in pairs:
        x -= w
        if x < 0:
            return v
    return pairs[-1][0]


def random_time_of_day(rng, day):
    hour = rng.choices(range(24), weights=HOUR_WEIGHTS)[0]
    return datetime(day.year, day.month, day.day, hour,
                    rng.randrange(60), rng.randrange(60))


def ramp(day, start, days_to_full):
    """0 before start, then linear up to 1 after days_to_full days."""
    if day < start:
        return 0.0
    return min(1.0, ((day - start).days + 1) / float(days_to_full))


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class User(object):
    __slots__ = ("user_id", "created_at", "company_id", "language",
                 "activated_at", "state", "country", "user_type", "level",
                 "devices", "churn_date", "ab_coin", "digest_minute",
                 "last_run_day", "treated_at", "group", "signup_steps")


def make_company_picker(rng):
    # Zipf-like company sizes: a few big companies, a long tail.
    ids = list(range(1, 13001))
    weights = [1.0 / (k ** 1.05) for k in ids]
    cum = []
    s = 0.0
    for w in weights:
        s += w
        cum.append(s)

    def pick():
        x = rng.random() * s
        lo, hi = 0, len(cum) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cum[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        return ids[lo]
    return pick


def generate_users(rng):
    pick_company = make_company_picker(rng)
    total_days = (USERS_END - USERS_START).days
    raw = []
    for day in daterange(USERS_START, USERS_END):
        t = (day - USERS_START).days / float(total_days)
        rate = 14 + 56 * (t ** 1.3)
        if day.weekday() >= 5:
            rate *= 0.25
        for _ in range(poisson(rng, rate)):
            raw.append(random_time_of_day(rng, day))
    raw.sort()

    users = []
    for uid, created in enumerate(raw):
        u = User()
        u.user_id = uid
        u.created_at = created
        u.company_id = pick_company()
        u.language = weighted(rng, LANGUAGES)
        u.country = weighted(rng, COUNTRIES_BY_LANGUAGE[u.language])

        # Signup funnel: create_user -> enter_email -> enter_info -> complete
        t_email = created + timedelta(seconds=rng.randint(15, 90))
        t_info = t_email + timedelta(seconds=rng.randint(40, 200))
        t_done = t_info + timedelta(seconds=rng.randint(20, 120))
        r = rng.random()
        if r < 0.50:
            u.state = "active"
            u.activated_at = t_done
            u.signup_steps = [("create_user", created), ("enter_email", t_email),
                              ("enter_info", t_info),
                              ("complete_signup", t_done)]
        else:
            u.state = "pending"
            u.activated_at = None
            steps = [("create_user", created), ("enter_email", t_email)]
            if r < 0.80:
                steps.append(("enter_info", t_info))
            u.signup_steps = steps

        # Activity level / user type.
        r = rng.random()
        if r < 0.20:
            u.user_type, u.level = 1, rng.uniform(0.12, 0.24)
        elif r < 0.60:
            u.user_type, u.level = 2, rng.uniform(0.04, 0.09)
        else:
            u.user_type, u.level = 3, rng.uniform(0.01, 0.03)

        # Devices: (device, weight).
        devs = []
        if rng.random() < 0.92:
            devs.append((rng.choice(COMPUTERS), 6.0))
        if rng.random() < 0.60:
            devs.append((rng.choice(PHONES), 3.0))
        if rng.random() < 0.28:
            devs.append((rng.choice(TABLETS), 1.5))
        if not devs:
            devs.append((rng.choice(COMPUTERS), 6.0))
        u.devices = devs

        # Lifetime: after churn_date the user stops using the product.
        if u.activated_at is not None:
            life = int(rng.expovariate(1.0 / 200.0)) + 7
            u.churn_date = u.activated_at.date() + timedelta(days=life)
        else:
            u.churn_date = None

        u.ab_coin = rng.random() < 0.5
        u.digest_minute = rng.randint(6 * 60, 10 * 60)
        # Start the "recent full search" state near its steady level, so
        # May does not look different from later months.
        u.last_run_day = None
        if u.activated_at is not None and rng.random() < 0.30:
            u.last_run_day = EVENTS_START - timedelta(days=rng.randint(1, 30))
        u.treated_at = None
        u.group = None
        users.append(u)
    return users


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def event_location(rng, u):
    if rng.random() < 0.93:
        return u.country
    return rng.choice(ALL_COUNTRIES)


def pick_device(rng, u):
    return weighted(rng, u.devices)


def build_session_tokens(rng, u, day, kind, in_test):
    """Return a list of event names for one session (without timestamps)."""
    age = (day - u.activated_at.date()).days
    tokens = []
    if kind == "normal" and rng.random() < 0.80:
        tokens.append("login")
    tokens.append("home_page")

    n_actions = 1 + poisson(rng, 2.2 if kind == "normal" else 1.4)
    for _ in range(n_actions):
        tokens.append(weighted(rng, [("view_inbox", 35), ("like_message", 25),
                                     ("home_page", 22), ("send_message", 18)]))

    # New users post less while they learn the product.
    keep_send = min(1.0, 0.30 + age / 40.0)
    out = []
    for tk in tokens:
        if tk == "send_message":
            if rng.random() > keep_send:
                continue
            out.append(tk)
            # A/B treatment: the new publisher makes people post more.
            if in_test and rng.random() < 0.06:
                out.append("send_message")
        else:
            out.append(tk)
    tokens = out

    # Autocomplete: used in about a quarter of sessions, once or twice.
    if rng.random() < 0.25:
        n_auto = weighted(rng, [(1, 60), (2, 27), (3, 9), (4, 4)])
        for _ in range(n_auto):
            tokens.insert(rng.randint(1, len(tokens)), "search_autocomplete")

    # Full search: ~8% of sessions. Users who ran a full search in the last
    # 30 days rarely try again (bad experience).
    recent = (u.last_run_day is not None and (day - u.last_run_day).days <= 30)
    p_run = 0.025 if recent else 0.13
    if rng.random() < p_run:
        u.last_run_day = day
        n_runs = weighted(rng, [(1, 12), (2, 22), (3, 24), (4, 18), (5, 10),
                                (6, 7), (7, 4), (8, 3)])
        block = ["search_run"] * n_runs
        # Clicks are rare, do not grow with the number of runs, and are
        # spread evenly across result positions 1-10 (poor ranking).
        if rng.random() < 0.22:
            n_clicks = 1 if rng.random() < 0.75 else 2
            for _ in range(n_clicks):
                pos = rng.randint(1, n_runs)
                block.insert(pos, "search_click_result_%d" % rng.randint(1, 10))
        tokens.insert(rng.randint(1, len(tokens)), "__SEARCH__")
        i = tokens.index("__SEARCH__")
        tokens[i:i + 1] = block
    return tokens


def emit_session(rng, u, start, device, tokens, sink):
    """Give timestamps to tokens (gaps < 10 min). Return end time."""
    t = start
    loc = event_location(rng, u)
    for i, name in enumerate(tokens):
        if i > 0:
            gap = min(540, 5 + int(rng.expovariate(1.0 / 55.0)))
            t = t + timedelta(seconds=gap)
        if t >= END_TS:
            break
        sink.append((t, u.user_id, "engagement", name, loc, device,
                     u.user_type))
    return t


def phone_broken(u, day, device):
    """Mobile app problem in August 2014 for long-time users."""
    cls = DEVICE_CLASS[device]
    if cls == "computer":
        return 0.0
    age = (day - u.activated_at.date()).days
    if age < 70:
        return 0.0
    strength = ramp(day, DROP_START, 10)
    return strength * (0.90 if cls == "phone" else 0.50)


DIGEST_CLICK_BASE = 0.60


def digest_click_rate(day):
    """P(clickthrough | open) for the weekly digest. Drops in August."""
    return DIGEST_CLICK_BASE - 0.50 * ramp(day, DROP_START, 6)


def simulate(rng, users):
    events = []
    emails = []
    experiments = []

    for u in users:
        # Signup funnel events inside the events window.
        if u.created_at.date() >= EVENTS_START:
            dev = pick_device(rng, u)
            loc = event_location(rng, u)
            for name, ts in u.signup_steps:
                events.append((ts, u.user_id, "signup_flow", name, loc, dev,
                               u.user_type))
        if u.activated_at is None:
            continue

        act_day = u.activated_at.date()
        new_in_ab = AB_START <= act_day < AB_END
        if act_day >= AB_START:
            ab_eligible_group = "control_group"  # the bug: new users -> control
        else:
            ab_eligible_group = "test_group" if u.ab_coin else "control_group"

        first_day = max(act_day, EVENTS_START)
        for day in daterange(first_day, EVENTS_END):
            age = (day - act_day).days
            alive = day < u.churn_date
            in_ab = AB_START <= day < AB_END
            in_test = (in_ab and u.treated_at is not None
                       and u.group == "test_group")

            # ---- intrinsic sessions --------------------------------------
            starts = []
            if day == act_day:
                starts.append(u.activated_at + timedelta(
                    seconds=rng.randint(10, 90)))
            elif alive:
                p = u.level * (1.0 + 4.0 * math.exp(-age / 21.0))
                if day.weekday() >= 5:
                    p *= 0.30
                if in_test:
                    p *= 1.35
                p = min(p, 0.95)
                if rng.random() < p:
                    k = weighted(rng, [(1, 64), (2, 26), (3, 10)])
                    for _ in range(k):
                        starts.append(random_time_of_day(rng, day))
            starts.sort()
            last_end = None
            for st in starts:
                if last_end is not None and st < last_end + timedelta(minutes=20):
                    st = last_end + timedelta(minutes=rng.randint(20, 90))
                if st.date() != day:
                    continue
                device = pick_device(rng, u)
                if rng.random() < phone_broken(u, day, device):
                    continue
                force_login = (in_ab and u.treated_at is None)
                in_test = (in_ab and u.treated_at is not None
                           and u.group == "test_group")
                tokens = build_session_tokens(rng, u, day, "normal", in_test)
                if force_login and tokens[0] != "login":
                    tokens.insert(0, "login")
                if in_ab and u.treated_at is None:
                    # First login in June: the user is put in a group.
                    u.treated_at = st
                    u.group = ab_eligible_group
                    experiments.append((st, u.user_id, "publisher_update",
                                        u.group, event_location(rng, u),
                                        device))
                last_end = emit_session(rng, u, st, device, tokens, events)

            # ---- weekly digest email (Mondays) ---------------------------
            if day.weekday() == 0 and alive and day > act_day:
                sent = datetime(day.year, day.month, day.day) + timedelta(
                    minutes=u.digest_minute, seconds=rng.randrange(60))
                emails.append((sent, u.user_id, "sent_weekly_digest",
                               u.user_type))
                if rng.random() < 0.46:
                    opened = sent + timedelta(seconds=rng.randint(5, 280))
                    emails.append((opened, u.user_id, "email_open",
                                   u.user_type))
                    r = rng.random()
                    ab_test = (in_ab and u.group == "test_group"
                               and u.treated_at is not None)
                    if r < digest_click_rate(day):
                        clicked = opened + timedelta(
                            seconds=rng.randint(5, 280))
                        emails.append((clicked, u.user_id,
                                       "email_clickthrough", u.user_type))
                        device = pick_device(rng, u)
                        tokens = build_session_tokens(rng, u, day, "email",
                                                      ab_test)
                        emit_session(rng, u,
                                     clicked + timedelta(seconds=rng.randint(2, 30)),
                                     device, tokens, events)
                    elif r < DIGEST_CLICK_BASE and age < 70:
                        # The digest link is broken in August. Newer users
                        # are habitual and come back on their own a bit
                        # later; long-time users depend on the email and
                        # do not come back.
                        st = opened + timedelta(minutes=rng.randint(30, 240))
                        device = pick_device(rng, u)
                        if st.date() == day:
                            tokens = build_session_tokens(rng, u, day,
                                                          "normal", ab_test)
                            emit_session(rng, u, st, device, tokens, events)

            # ---- re-engagement email after churn -------------------------
            if not alive and (day - u.churn_date).days == 10:
                sent = random_time_of_day(rng, day)
                emails.append((sent, u.user_id, "sent_reengagement_email",
                               u.user_type))
                if rng.random() < 0.36:
                    opened = sent + timedelta(seconds=rng.randint(5, 280))
                    emails.append((opened, u.user_id, "email_open",
                                   u.user_type))
                    if rng.random() < 0.55:
                        clicked = opened + timedelta(
                            seconds=rng.randint(5, 280))
                        emails.append((clicked, u.user_id,
                                       "email_clickthrough", u.user_type))
                        device = pick_device(rng, u)
                        tokens = build_session_tokens(rng, u, day, "email",
                                                      False)
                        emit_session(rng, u,
                                     clicked + timedelta(seconds=rng.randint(2, 30)),
                                     device, tokens, events)

    events = [e for e in events if e[0] < END_TS]
    emails = [e for e in emails if e[0] < END_TS]
    return events, emails, experiments


# ---------------------------------------------------------------------------
# Rollup periods
# ---------------------------------------------------------------------------

def pst_offset_hours(ts):
    """Hours to add to Pacific local time to get UTC (US DST rules)."""
    y = ts.year
    # DST: second Sunday in March 02:00 to first Sunday in November 02:00.
    march = date(y, 3, 1)
    dst_start = march + timedelta(days=(6 - march.weekday()) % 7 + 7)
    nov = date(y, 11, 1)
    dst_end = nov + timedelta(days=(6 - nov.weekday()) % 7)
    start = datetime(dst_start.year, dst_start.month, dst_start.day, 2)
    end = datetime(dst_end.year, dst_end.month, dst_end.day, 2)
    return 7 if start <= ts < end else 8


def rollup_rows():
    rows = []
    for period_id, length in ((1001, 1), (1007, 7), (1028, 28)):
        for d in daterange(date(2013, 1, 1), date(2014, 12, 31)):
            pst_end = datetime(d.year, d.month, d.day)
            pst_start = pst_end - timedelta(days=length)
            utc_start = pst_start + timedelta(hours=pst_offset_hours(pst_start))
            utc_end = pst_end + timedelta(hours=pst_offset_hours(pst_end))
            rows.append((period_id, d.isoformat(), fmt(pst_start),
                         fmt(pst_end), fmt(utc_start), fmt(utc_end)))
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: generate_yammer.py OUTPUT_DIR\n")
        return 2
    out = argv[1]
    os.makedirs(out, exist_ok=True)
    rng = random.Random(SEED)

    users = generate_users(rng)
    events, emails, experiments = simulate(rng, users)

    events.sort(key=lambda e: (e[0], e[1]))
    emails.sort(key=lambda e: (e[0], e[1]))
    experiments.sort(key=lambda e: (e[0], e[1]))

    write_csv(os.path.join(out, "yammer_users.csv"),
              ["user_id", "created_at", "company_id", "language",
               "activated_at", "state"],
              ((u.user_id, fmt(u.created_at), u.company_id, u.language,
                fmt(u.activated_at) if u.activated_at else "", u.state)
               for u in users))
    write_csv(os.path.join(out, "yammer_events.csv"),
              ["user_id", "occurred_at", "event_type", "event_name",
               "location", "device", "user_type"],
              ((e[1], fmt(e[0]), e[2], e[3], e[4], e[5], e[6])
               for e in events))
    write_csv(os.path.join(out, "yammer_emails.csv"),
              ["user_id", "occurred_at", "action", "user_type"],
              ((e[1], fmt(e[0]), e[2], e[3]) for e in emails))
    write_csv(os.path.join(out, "yammer_experiments.csv"),
              ["user_id", "occurred_at", "experiment", "experiment_group",
               "location", "device"],
              ((e[1], fmt(e[0]), e[2], e[3], e[4], e[5])
               for e in experiments))
    write_csv(os.path.join(out, "dimension_rollup_periods.csv"),
              ["period_id", "time_id", "pst_start", "pst_end", "utc_start",
               "utc_end"],
              rollup_rows())

    print("users=%d events=%d emails=%d experiments=%d"
          % (len(users), len(events), len(emails), len(experiments)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
