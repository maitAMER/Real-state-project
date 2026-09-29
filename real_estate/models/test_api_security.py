import xmlrpc.client

url = 'http://localhost:8017'
db = 'test17'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
if not uid:
    raise SystemExit(
        f"Odoo login failed for user '{username}' on database '{db}'. "
        'Check the database name and the user login/password.'
    )

print(f"Logged in as user Name: {username} and User ID: {uid}")
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

tenant_ids = models.execute_kw(
    db, uid, password,
    'real_estate.tenant', 'search',
    [[]], {'limit': 1}
)
print(f"Found tenant: {tenant_ids}")

tenant_data = models.execute_kw(
    db, uid, password,
    'real_estate.tenant', 'read',
    [tenant_ids, ['name', 'phone', 'email']]
)
print(f"Tenant data: {tenant_data}")

# Update record
models.execute_kw(
    db, uid, password,
    'real_estate.tenant', 'write',
    [[tenant_ids[0]], {'phone': '+1234567890'}]
)