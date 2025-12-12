import logging
import re
from typing import Optional

import ldap3
from django.conf import settings
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


AD_DATA_MAP = {
    "52d": "Senha não atende à política (complexidade/tamanho/histórico) ou outra restrição.",
    "773": "Usuário deve trocar a senha no próximo logon (pwdLastSet=0).",
    "775": "Conta bloqueada (lockout).",
    "533": "Conta desabilitada.",
    "701": "Conta expirada.",
    "532": "Senha expirada.",
    "5": "Acesso negado (permissões insuficientes para resetar).",
    "56": "Senha atual incorreta (quando troca exige old_password).",
}


def explain_ad_ldap_result(result: dict) -> str:
    msg = (result or {}).get("message") or ""
    m = re.search(r"data\s+([0-9a-fA-F]{1,8})", msg)
    if not m:
        return msg.strip() or "Sem detalhes no 'message' do LDAP."
    code = m.group(1).lstrip("0").lower() or "0"
    return f"Causa: {AD_DATA_MAP.get(code, 'código data desconhecido')} (data={code})"


WIN32_MAP = {
    "0000052d": "A sua senha não pode ser uma senha usada anteriormente e não pode conter partes do seu nome de usuário ou nome completo.",
    "00000773": "Usuário deve trocar a senha no próximo logon",
    "00000775": "Conta bloqueada",
    "00000056": "Erro de autenticação: senha incorreta",
    "00000533": "Conta desabilitada",
    "00000701": "Conta expirada",
    "00000532": "Senha expirada",
    "00000005": "Acesso negado",
}


def explain_ad_message(result: dict) -> str:
    msg = (result or {}).get("message") or ""
    match_1 = re.search(r"\b([0-9a-fA-F]{8})\b", msg)

    if match_1:
        code8 = match_1.group(1).lower()
        if code8 in WIN32_MAP:
            return f"Causa: {WIN32_MAP[code8]}"

    match_2 = re.search(r"data\s+([0-9a-fA-F]{1,8})", msg)
    if match_2:
        return f"Causa: data={match_2.group(1).lower()}"
    return msg.strip() or "Sem detalhes no 'message' do LDAP."


class ADResetPass:
    def __init__(self):
        self.connection = None
        self.ldap_url = settings.LDAP_URL
        self.ldap_port = settings.LDAP_PORT
        self.ldap_domain = settings.LDAP_DOMAIN
        self.ldap_username = settings.LDAP_SERVICE_SAM_ACCOUNT_NAME
        self.ldap_password = settings.LDAP_SERVICE_PASSWORD
        self.ldap_logon_domain_name = settings.LDAP_LOGON_DOMAIN_NAME

    def reset_password(
        self,
        user_dn: str,
        new_password: str,
        old_password: Optional[str] = None,
    ) -> str:
        self._get_connection()
        self._auth_service_ldap_user()

        if self.connection is None:
            return _("LDAP Connection is empty")

        ok = self.connection.extend.microsoft.modify_password(
            user_dn, new_password, old_password=old_password
        )

        if not ok:
            result = self.connection.result or {}
            logger.warning(
                "AD password rejected",
                extra={"user_dn": user_dn, "ldap_result": result},
            )
            return explain_ad_message(result)

        return ""

    def _get_connection(self) -> None:
        server = ldap3.Server(
            host=self.ldap_url,
            port=self.ldap_port,
            use_ssl=True,
            get_info=ldap3.ALL,
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
        if not self.connection.bind():
            print("error", "The service account failed to login")
        else:
            print("The service account logged in successfully")
