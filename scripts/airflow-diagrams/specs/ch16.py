from lib import N, E, Z, T
D = {}

D["ch16-security-layers"] = dict(items=[
    N("user", "Пользователь\nв браузере", 0, 0, "n"),
    N("ldap", "LDAP / Entra ID\nединые учётные записи", 350, 0, "y"),
    N("api", "API server (UI)\nRBAC: роли и права", 0, 150, "p"),
    N("db", "Metastore\nсекреты под Fernet key", 0, 300, "db"),
    N("vault", "Secrets backend\nVault, AWS SSM", 350, 300, "pu"),
    T("Каждый слой уменьшает attack surface", 0, 440),
], edges=[
    E("user", "api", "HTTPS (TLS)"),
    E("api", "ldap", "bind + search"),
    E("api", "db", "encrypt / decrypt"),
    E("api", "vault", "conn_uri, value"),
])

D["ch16-secrets-lookup"] = dict(items=[
    N("task", "Task просит\nconnection по conn_id", 0, 0, "n"),
    N("backend", "1. Secrets backend\n(Vault, SSM, ...)", 0, 150, "pu"),
    N("env", "2. Переменные среды\nAIRFLOW_CONN_*", 0, 300, "y"),
    N("meta", "3. Metastore\n(Fernet-шифрование)", 0, 450, "db"),
    N("found", "Секрет найден", 350, 300, "g"),
], edges=[
    E("task", "backend"),
    E("backend", "env", "не найден"),
    E("env", "meta", "не найден"),
    E("env", "found", "найден", dashed=True),
])
