from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, QueryDict
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.core.services.ldap.change_password import ADResetPass
from apps.core.services.ldap.search_user import SearchLDAPUser
from apps.core.services.mail.send_mail import MailService


def index(request: HttpRequest):
    return redirect("password")


class PasswordView(View):
    def get(self, request: HttpRequest):
        enterprise_name = settings.ENTERPRISE_NAME
        template_name = "password.html"
        context = {"enterprise_name": enterprise_name}
        return render(request, template_name, context)

    def post(self, request: HttpRequest):
        template_name = "password.html"
        enterprise_name = settings.ENTERPRISE_NAME
        data = request.POST

        if not self.validate_data(request, data):
            context = {}
            context["enterprise_name"] = enterprise_name
            context["username"] = data.get("username")
            context["current_password"] = data.get("current_password")
            context["new_password"] = data.get("new_password")
            context["repeate_password"] = data.get("repeate_password")
            return render(request, template_name, context)

        self.change_ldap_password(request, data)
        return redirect("password")

    def password_valid_complexity(self, request: HttpRequest, password: str):
        is_valid = True
        has_special_chars = False
        especial_chars = [
            "!",
            "#",
            "$",
            "&",
            "(",
            ")",
            "*",
            "+",
            "-",
            "/",
            ":",
            ";",
            "<",
            "=",
            ">",
            "@",
        ]
        if len(password) < 8:
            is_valid = False
            messages.add_message(
                request,
                messages.ERROR,
                _("minimum 8 characters"),
            )

        for letter in password:
            if letter in especial_chars:
                has_special_chars = True
                break

        if not has_special_chars:
            is_valid = False
            messages.add_message(
                request,
                messages.ERROR,
                _("Use special character"),
            )

        return is_valid

    def change_ldap_password(self, request: HttpRequest, data: QueryDict):
        username = data.get("username") or ""
        current_password = data.get("current_password") or ""
        new_password = data.get("new_password") or ""
        ldap_search = SearchLDAPUser()
        response = ldap_search.search_user_dn_by_username(username=username)

        if "CN" not in response:
            messages.add_message(request, messages.SUCCESS, response)
            return False

        user_dn = response
        ad_reset_pass = ADResetPass()
        error_message = ad_reset_pass.reset_password(
            user_dn=user_dn,
            old_password=current_password,
            new_password=new_password,
        )

        if error_message != "":
            messages.add_message(request, messages.ERROR, error_message)
            return False

        messages.add_message(
            request,
            messages.ERROR,
            _("Successfully updated password"),
        )
        return True

    def validate_data(self, request: HttpRequest, data: QueryDict):
        username = data.get("username")
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        repeate_password = data.get("repeate_password")
        is_valid = True

        if username is None or len(username) == 0:
            messages.add_message(
                request,
                messages.WARNING,
                _("Username is required"),
            )
            is_valid = False
        if current_password is None or len(current_password) == 0:
            messages.add_message(
                request,
                messages.WARNING,
                _("Current password is required"),
            )
            is_valid = False
        if new_password is None or len(new_password) == 0:
            messages.add_message(
                request,
                messages.WARNING,
                _("New password is required"),
            )
            is_valid = False
        if repeate_password is None or len(repeate_password) == 0:
            messages.add_message(
                request,
                messages.WARNING,
                _("Repeat password is required"),
            )
            is_valid = False
        if is_valid:
            if new_password != repeate_password:
                messages.add_message(
                    request,
                    messages.WARNING,
                    _("Different passwords"),
                )
                is_valid = False

        if is_valid:
            is_valid = self.password_valid_complexity(
                request,
                new_password or "",
            )

        return is_valid


class RequestMailView(View):
    def get(self, request: HttpRequest):
        self.clear_session_data(request)
        enterprise_name = settings.ENTERPRISE_NAME
        template_name = "mail.html"
        context = {"enterprise_name": enterprise_name}
        return render(request, template_name, context)

    def post(self, request: HttpRequest):
        template_name = "mail.html"
        enterprise_name = settings.ENTERPRISE_NAME
        data = request.POST
        username = data.get("username") or ""

        if not self.validate_username(username=username):
            context = {}
            messages.add_message(
                request,
                messages.ERROR,
                _("Username is required"),
            )
            context["enterprise_name"] = enterprise_name
            return render(request, template_name, context)

        mail_response = self.send_token_to_mail(
            request=request,
            username=username,
        )
        if not mail_response:
            return redirect("mail")

        return redirect("token")

    def validate_username(self, username: str) -> bool:
        has_username = username is not None and len(username) > 0
        return has_username

    def send_token_to_mail(self, request: HttpRequest, username: str):
        ldap_search = SearchLDAPUser()
        mail_response = ldap_search.search_mail_by_username(username=username)

        if "@" not in mail_response:
            messages.add_message(request, messages.WARNING, mail_response)
            return False

        token = str(uuid4())
        mail_service = MailService()
        mail_service.send_token(to=mail_response, token=token)

        request.session["token"] = token
        request.session["username"] = username
        messages.add_message(
            request,
            messages.SUCCESS,
            _("The token has been sent to your e-mail"),
        )
        return True

    def clear_session_data(self, request: HttpRequest):
        request.session.clear()


class ConfirmTokenView(View):
    def get(self, request: HttpRequest):
        enterprise_name = settings.ENTERPRISE_NAME
        template_name = "token.html"
        username = request.session.get("username") or ""

        if len(username) == 0:
            return redirect("mail")
        context = {
            "enterprise_name": enterprise_name,
            "username": username,
        }
        return render(request, template_name, context)

    def post(self, request: HttpRequest):
        data = request.POST
        received_token = data.get("token") or ""
        username = request.session.get("username") or ""
        new_password = self.get_new_password()

        if not self.validate_token(request, received_token, username):
            return redirect("token")

        if not self.update_user_password(request, username, new_password):
            return redirect("token")

        if not self.send_password_to_mail(request, username, new_password):
            return redirect("token")

        messages.add_message(
            request,
            messages.SUCCESS,
            _("Your new password has been sent to your e-mail"),
        )

        return redirect("password")

    def get_new_password(self):
        uuid = str(uuid4())
        password = uuid.replace("-", "")
        if len(password) > 12:
            left = password[0:6]
            right = password[6:11]
            password = left + "@" + right
            return password
        return password

    def send_password_to_mail(
        self,
        request: HttpRequest,
        username: str,
        password: str,
    ):
        ldap_search = SearchLDAPUser()
        mail_response = ldap_search.search_mail_by_username(username=username)

        if "@" not in mail_response:
            messages.add_message(request, messages.WARNING, mail_response)
            return False

        mail_service = MailService()
        mail_service.send_password(to=mail_response, password=password)
        return True

    def validate_token(
        self, request: HttpRequest, received: str, username: str
    ) -> bool:
        saved_token = request.session.get("token") or ""
        has_received_token = len(received) > 0
        has_saved_token = len(saved_token) > 0
        has_usernme = len(username) > 0

        if not has_received_token or not has_saved_token or not has_usernme:
            messages.add_message(
                request,
                messages.ERROR,
                _("Invalid Token"),
            )
            return False

        return received == saved_token

    def update_user_password(
        self,
        request: HttpRequest,
        username: str,
        password: str,
    ) -> bool:
        ldap_search = SearchLDAPUser()
        user_dn = ldap_search.search_user_dn_by_username(username=username)

        if "CN" not in user_dn:
            messages.add_message(request, messages.SUCCESS, user_dn)
            return False

        ad_reset_pass = ADResetPass()
        error_message = ad_reset_pass.reset_password(
            user_dn=user_dn,
            new_password=password,
        )

        if error_message != "":
            messages.add_message(request, messages.ERROR, error_message)
            return False

        return True
