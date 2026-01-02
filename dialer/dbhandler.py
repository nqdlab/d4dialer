from django.db import connections

def execute(cmd):
    cursor = connections['fusionpbx'].cursor()
    cursor.execute(cmd)
    rows = cursor.fetchall()
    return rows

def get_ivr_menu_names():
    rows =  execute("select ivr_menu_name from v_ivr_menus;")
    return [r[0] for r in rows]

def get_sip_gateway_names():
    rows =  execute("select gateway from v_gateways;")
    return [r[0] for r in rows]

def get_ivr_menu_extension(ivr_menu_name):
    rows = execute(f"select ivr_menu_extension from v_ivr_menus where ivr_menu_name='{ivr_menu_name}';")
    if rows:
        return rows[0][0]
    return None

def get_domain_uuid(ivr_menu_name):
    rows = execute(f"select domain_uuid from v_ivr_menus where ivr_menu_name='{ivr_menu_name}';")
    if rows:
        return rows[0][0]
    return None

def get_domain_name(domain_uuid):
    rows = execute(f"select domain_name from v_domains where domain_uuid='{domain_uuid}';")
    if rows:
        return rows[0][0]
    return None

def get_api_keys():
    rows = execute("select api_key from v_users;")
    return [r[0] for r in rows]