from django.contrib import messages
from django.http import HttpRequest, QueryDict
from django.utils.translation import gettext as _


def password_valid_complexity(request: HttpRequest, password: str):
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
        ".",
        "_",
    ]
    if len(password) < 9:
        is_valid = False
        messages.add_message(
            request,
            messages.ERROR,
            _("minimum 9 characters"),
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


def validate_change_password_data(request: HttpRequest, data: QueryDict):
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
        is_valid = password_valid_complexity(
            request,
            new_password or "",
        )

    return is_valid


def validate_token_password_data(request: HttpRequest, data: QueryDict):
    new_password = data.get("new_password")
    repeate_password = data.get("repeate_password")
    is_valid = True

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
        is_valid = password_valid_complexity(
            request,
            new_password or "",
        )

    return is_valid
