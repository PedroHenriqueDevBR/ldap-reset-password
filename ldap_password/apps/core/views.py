from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, QueryDict
from django.shortcuts import redirect, render
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

    def change_ldap_password(self, request: HttpRequest, data: QueryDict):
        username = data.get("username") or ""
        current_password = data.get("current_password") or ""
        new_password = data.get("new_password") or ""
        # Get user DN
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
                "Username is required",
            )
            is_valid = False
        if current_password is None or len(current_password) == 0:
            messages.add_message(
                request,
                messages.WARNING,
                "Current password is required",
            )
            is_valid = False
        if new_password is None or len(new_password) == 0:
            messages.add_message(
                request,
                messages.WARNING,
                "New password is required",
            )
            is_valid = False
        if repeate_password is None or len(repeate_password) == 0:
            messages.add_message(
                request,
                messages.WARNING,
                "Repeat password is required",
            )
            is_valid = False
        if is_valid:
            if new_password != repeate_password:
                messages.add_message(
                    request,
                    messages.WARNING,
                    "Different passwords",
                )
                is_valid = False
        return is_valid


class RequestMailView(View):
    def get(self, request: HttpRequest):
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
                "Username is required",
            )
            context["enterprise_name"] = enterprise_name
            return render(request, template_name, context)

        self.send_token_to_mail(request=request, username=username)
        return redirect("mail")

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
        mail_service.send_mail(to=mail_response, token=token)
        request.session["token"] = token

        return True
