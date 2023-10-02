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
from apps.core.validators.validate_password_form import (
    validate_token_password_data,
    validate_change_password_data,
)


def index(request: HttpRequest):
    template_name = "options.html"
    return render(request, template_name)


def success(request: HttpRequest):
    template_name = "success.html"
    redirect_url = settings.SUCCESS_REDIRECT_URL
    context = {"redirect_url": redirect_url}
    return render(request, template_name, context)


class PasswordView(View):
    def get(self, request: HttpRequest):
        enterprise_name = settings.ENTERPRISE_NAME
        template_name = "password.html"
        context = {"enterprise_name": enterprise_name}
        return render(request, template_name, context)

    def post(self, request: HttpRequest):
        template_name = "password.html"
        data = request.POST

        if not validate_change_password_data(request, data):
            context = self.create_context(data=data)
            return render(request, template_name, context)

        success = self.change_ldap_password(request, data)
        if not success:
            context = self.create_context(data=data)
            return render(request, template_name, context)

        return redirect("success")

    def create_context(self, data: QueryDict):
        context = {}
        enterprise_name = settings.ENTERPRISE_NAME
        context["enterprise_name"] = enterprise_name
        context["username"] = data.get("username")
        context["current_password"] = data.get("current_password")
        context["new_password"] = data.get("new_password")
        context["repeate_password"] = data.get("repeate_password")
        return context

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

        return True


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

        request.session["new_password"] = new_password
        # if not self.update_user_password(request, username, new_password):
        #     return redirect("token")

        return redirect("token_password")

    def get_new_password(self):
        uuid = str(uuid4())
        password = uuid.replace("-", "")
        if len(password) > 12:
            left = password[0:6]
            right = password[6:11]
            password = left + "@" + right
            return password
        return password

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


class ChangePasswordToken(View):
    def get(self, request: HttpRequest):
        enterprise_name = settings.ENTERPRISE_NAME
        template_name = "token_password.html"
        username = request.session.get("username") or ""
        new_password = request.session.get("new_password") or ""
        saved_token = request.session.get("token") or ""

        has_saved_token = len(saved_token) > 0
        has_username = len(username) > 0
        has_new_password = len(new_password) > 0

        if not has_username or not has_new_password or not has_saved_token:
            return redirect("mail")

        context = {
            "enterprise_name": enterprise_name,
            "username": username,
        }

        return render(request, template_name, context)

    def post(self, request: HttpRequest):
        data = request.POST
        template_name = "token_password.html"
        username = request.session.get("username") or ""
        saved_token = request.session.get("token") or ""

        has_username = len(username) > 0
        has_saved_token = len(saved_token) > 0

        if not has_username or not has_saved_token:
            messages.add_message(
                request,
                messages.WARNING,
                _("Invalid Token"),
            )
            return redirect("mail")

        if not validate_token_password_data(request=request, data=data):
            context = self.create_context(data=data)
            return render(request, template_name, context)

        success = self.change_ldap_password(
            request=request,
            username=username,
            data=data,
        )

        if not success:
            context = self.create_context(data=data)
            return render(request, template_name, context)

        return redirect("success")

    def create_context(self, data: QueryDict):
        enterprise_name = settings.ENTERPRISE_NAME
        context = {}
        context["enterprise_name"] = enterprise_name
        context["new_password"] = data.get("new_password")
        context["repeate_password"] = data.get("repeate_password")
        return context

    def change_ldap_password(
        self,
        request: HttpRequest,
        username: str,
        data: QueryDict,
    ):
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
            new_password=new_password,
        )

        if error_message != "":
            messages.add_message(request, messages.ERROR, error_message)
            return False

        self.clear_session_data(request=request)
        return True

    def clear_session_data(self, request: HttpRequest):
        request.session.clear()
