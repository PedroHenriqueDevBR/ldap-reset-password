import json
from typing import Optional

from django.conf import settings
import ldap3
from ldap3 import ALL, SUBTREE, Connection, Server
from ldap3.core.exceptions import LDAPSocketOpenError


class SearchLDAPUser:
    def __init__(self):
        self.ldap: Optional[Connection] = None
        self.ldap_url = settings.LDAP_URL
        self.ldap_port = settings.LDAP_PORT
        self.ldap_base = settings.LDAP_BASE
        self.ldap_domain = settings.LDAP_DOMAIN
        self.ldap_logon_domain = settings.LDAP_LOGON_DOMAIN_NAME
        self.ldap_username = settings.LDAP_SERVICE_SAM_ACCOUNT_NAME
        self.ldap_password = settings.LDAP_SERVICE_PASSWORD

    def _get_user_principal_name(self, username):
        if "@" in username:
            return username
        return f"{username}@{self.ldap_domain}"

    def _get_connection(self):
        ldap_server = Server(
            host=self.ldap_url,
            port=self.ldap_port,
            get_info=ALL,
            use_ssl=True if self.ldap_url == 636 else False,
        )
        self.ldap = Connection(
            ldap_server,
            user=self.ldap_username,
            password=self.ldap_password,
        )
        self.ldap.authentication = ldap3.NTLM
        self.ldap.user = f"{self.ldap_logon_domain}\\{self.ldap_username}"
        self.ldap.password = self.ldap_password

    def _execute_search(self, user):
        if self.ldap is None:
            return False
        return self.ldap.search(
            search_base=self.ldap_base,
            search_filter=f"(userPrincipalName={user})",
            search_scope=SUBTREE,
            attributes=[
                "uid",
                "mail",
            ],
        )

    def _search(self, username) -> Optional[dict]:
        try:
            self._get_connection()
            user_search = self._get_user_principal_name(username=username)

            if self.ldap is None:
                raise ConnectionError()

            if self.ldap.bind() is False:
                raise ConnectionError()

            if self._execute_search(user=user_search) is False:
                raise IndexError()

            if len(self.ldap.entries) == 0:
                raise IndexError()

            entry = self.ldap.entries[0]
            json_data = entry.entry_to_json()
            data = json.loads(json_data)
            return data

        except IndexError as error:
            raise error
        except ConnectionError as error:
            raise error
        except LDAPSocketOpenError as error:
            raise error
        finally:
            if self.ldap is not None:
                self.ldap.unbind()

    def search_user_dn_by_username(self, username) -> str:
        try:
            response = self._search(username=username)
            if response is None:
                raise IndexError

            user_dn = response["dn"]
            return str(user_dn)
        except IndexError:
            return f"{username} Not found!"
        except ConnectionError:
            return "Can not search user data in LDAP Server!"
        except LDAPSocketOpenError:
            return "Can not connect to the LDAP server!"

    def search_mail_by_username(self, username) -> str:
        try:
            response = self._search(username=username)
            if response is None:
                raise IndexError

            attrs = response["attributes"]
            if "mail" in attrs:
                mail = attrs["mail"]
                if len(mail) > 0:
                    return mail[0]

            raise AttributeError
        except AttributeError:
            return "Mail not registered to user, contact your \
                    system administrator"
        except IndexError:
            return f"{username} Not found!"
        except ConnectionError:
            return "Can not search user data in LDAP Server!"
        except LDAPSocketOpenError:
            return "Unabled to connect to the LDAP server"
