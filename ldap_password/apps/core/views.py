from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.contrib import messages

from apps.core.ldap.search_user import SearchLDAPUser
from apps.core.ldap.change_password import ADResetPass


def index(request):
    return redirect("password")


class PasswordView(View):
    def get(self, request):
        enterprise_name = settings.ENTERPRISE_NAME
        template_name = "password.html"
        context = {"enterprise_name": enterprise_name}
        return render(request, template_name, context)

    def post(self, request):
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

        if self.change_ldap_password(request, data):
            messages.add_message(
                request,
                messages.SUCCESS,
                "Updated password!",
            )
        else:
            messages.add_message(
                request,
                messages.SUCCESS,
                "Error on update password!",
            )

        return redirect("password")

    def change_ldap_password(self, request, data):
        username = data.get("username")
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        # Get user DN
        ldap_search = SearchLDAPUser()
        response = ldap_search.search_user_dn_by_username(username=username)

        if "CN" not in response:
            messages.add_message(request, messages.SUCCESS, str(response))
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

    def validate_data(self, request, data):
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
