"""Контракт транзакций из главы 26. pandas 2.2.3, Pandera 0.22.1."""
import pandas as pd
import pandera as pa


def main():
    schema = pa.DataFrameSchema(
        {
            "transaction_id": pa.Column(
                str, unique=True, checks=pa.Check.str_matches(
                    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
                ),
            ),
            "account_id": pa.Column(str),
            "amount_cents": pa.Column(int, pa.Check.in_range(1, 100_000_000)),
            "currency_code": pa.Column(str, pa.Check.isin(["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF"])),
            "status": pa.Column(str, pa.Check.isin(["pending", "processing", "settled", "failed", "reversed"])),
            "created_at": pa.Column(pd.Timestamp),
            "settled_at": pa.Column(pd.Timestamp, nullable=True),
        },
        checks=pa.Check(
            lambda df: df.loc[df["settled_at"].notna(), "settled_at"]
            >= df.loc[df["settled_at"].notna(), "created_at"],
            error="settled_at must not be earlier than created_at",
        ),
        coerce=False,
    )
    payments = pd.DataFrame([{
        "id": "12345678-1234-4abc-8123-123456789abc",
        "account_id": "A-17",
        "amount_cents": 1450,
        "currency_code": "EUR",
        "status": "settled",
        "created_at": pd.Timestamp("2026-04-01"),
        "settled_at": pd.Timestamp("2026-04-02"),
    }]).rename(columns={"id": "transaction_id"})
    print("Корректных строк:", len(schema.validate(payments)))
    payments.loc[0, ["amount_cents", "currency_code"]] = [-10, "RUB"]
    try:
        schema.validate(payments, lazy=True)
    except pa.errors.SchemaErrors as error:
        fields = sorted(set(error.failure_cases["column"]))
        print("Нарушен контракт полей:", ", ".join(fields))


if __name__ == "__main__":
    main()
