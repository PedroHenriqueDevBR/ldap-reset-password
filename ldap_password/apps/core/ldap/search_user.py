import json

from django.conf import settings
from ldap3 import ALL, SUBTREE, Connection, Server
from ldap3.core.exceptions import LDAPSocketOpenError


class SearchLDAPUser:
    def __init__(self):
        self.ldap_url = settings.LDAP_URL
        self.ldap_port = settings.LDAP_PORT
        self.ldap_base = settings.LDAP_BASE
        self.ldap_domain = settings.LDAP_DOMAIN
        self.ldap_username = settings.LDAP_SERVICE_BIND_DN
        self.ldap_password = settings.LDAP_SERVICE_PASSWORD

    def _get_user_principal_name(self, username):
        if "@" in username:
            return username
        return f"{username}@{self.ldap_domain}"

    def search(self, username) -> str:
        try:
            ldap_server_uri = f"{self.ldap_url}:{self.ldap_port}"
            ldap_server = Server(ldap_server_uri, get_info=ALL)
            user_search = self._get_user_principal_name(username=username)

            ldap_connection = Connection(
                ldap_server,
                user=self.ldap_username,
                password=self.ldap_password,
            )
            if ldap_connection.bind() is True:
                if (
                    ldap_connection.search(
                        search_base=self.ldap_base,
                        search_filter=f"(userPrincipalName={user_search})",
                        search_scope=SUBTREE,
                        attributes=["uid"],
                    )
                    is True
                ):
                    if len(ldap_connection.entries) == 0:
                        return f"{username} Not found!"

                    entry = ldap_connection.entries[0]
                    json_data = entry.entry_to_json()
                    ldap_connection.unbind()
                    data = json.loads(json_data)
                    user_dn = data["dn"]
                    return str(user_dn)
                else:
                    print("Unabled to connect to the LDAP server!")
                    return "Unabled to connect to the LDAP server"
        except LDAPSocketOpenError:
            print("Unabled to connect to the LDAP server!")
            return "Unabled to connect to the LDAP server"
