from django.conf import settings
import ldap3


class ADResetPass:
    def __init__(self):
        self.connection = None
        self.ldap_url = settings.LDAP_URL
        self.ldap_port = settings.LDAP_PORT
        self.ldap_domain = settings.LDAP_DOMAIN
        self.ldap_username = settings.LDAP_SERVICE_SAM_ACCOUNT_NAME
        self.ldap_password = settings.LDAP_SERVICE_PASSWORD
        self.ldap_logon_domain_name = settings.LDAP_LOGON_DOMAIN_NAME

    def reset_password(self, user_dn, new_password, old_password) -> str:
        self._get_connection()
        self._auth_service_ldap_user()

        if self.connection is None:
            return "LDAP Connection is empty."

        response = self.connection.extend.microsoft.modify_password(
            user_dn,
            new_password,
            old_password=old_password,
        )
        if not response:
            return "Current password is incorrect."

        return ""

    def _get_connection(self) -> None:
        server = ldap3.Server(
            host=self.ldap_url,
            port=self.ldap_port,
            use_ssl=True,
        )
        self.connection = ldap3.Connection(server=server)
        self.connection.authentication = ldap3.NTLM

    def _auth_service_ldap_user(self) -> None:
        if self.connection is None:
            return None
        if self.connection.bound:
            print(
                "The login method was called but the connection is already \
                bound. Will reconnect."
            )
            self.connection.unbind()
            self.connection.open()

        username = self.ldap_username
        password = self.ldap_password
        domain = self.ldap_logon_domain_name
        if "@" in username or "\\" in username or "CN=" in username:
            self.connection.user = username
        else:
            if self.connection.authentication == ldap3.NTLM:
                self.connection.user = f"{domain}\\{username}"
            else:
                self.connection.user = f"{username}@{domain}"

        self.connection.password = password
        svc_account = self.ldap_username == username

        if not self.connection.bind():
            if svc_account:
                print("error", "The service account failed to login")
                return None
            else:
                print('The user "%s" failed to login', self.connection.user)
                print("Username or password is incorrect. Please try again")
                return None
        else:
            if svc_account:
                print("The service account logged in successfully")
            else:
                print("The user logged in successfully")
