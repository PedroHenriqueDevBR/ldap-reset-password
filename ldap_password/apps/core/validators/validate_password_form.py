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
            extra_tags="alert-danger",
        )
        is_valid = False
    if current_password is None or len(current_password) == 0:
        messages.add_message(
            request,
            messages.WARNING,
            _("Current password is required"),
            extra_tags="alert-danger",
        )
        is_valid = False
    if new_password is None or len(new_password) == 0:
        messages.add_message(
            request,
            messages.WARNING,
            _("New password is required"),
            extra_tags="alert-danger",
        )
        is_valid = False
    if repeate_password is None or len(repeate_password) == 0:
        messages.add_message(
            request,
            messages.WARNING,
            _("Repeat password is required"),
            extra_tags="alert-danger",
        )
        is_valid = False
    if is_valid:
        if new_password != repeate_password:
            messages.add_message(
                request,
                messages.WARNING,
                _("Different passwords"),
                extra_tags="alert-danger",
            )
            is_valid = False

    password_errors = _validate_password_rules(new_password or "")
    if len(password_errors) > 0:
        is_valid = False
        for error in password_errors:
            messages.add_message(
                request,
                messages.WARNING,
                "A senha deve ter: " + error,
                extra_tags="alert-danger",
            )

    if is_valid:
        is_valid = password_valid_complexity(
            request,
            new_password or "",
        )

    return is_valid


def _validate_password_rules(password: str):
    """
    Não conter o nome da conta ou mais de dois caracteres consecutivos de partes do nome completo do usuário
    Ter pelo menos 9 caracteres
    Conter caracteres de três destas quatro categorias:
            maiúsculos (A-Z)
            minúsculos (a-z)
            dígitos (0 a 9)
            especiais (!, $, #, %)
    """

    errors = []
    if len(password) < 9:
        errors.append("pelo menos 9 caracteres")
    if not any(c.islower() for c in password):
        errors.append("minúsculos (a-z)")
    if not any(c.isupper() for c in password):
        errors.append("maiúsculos (A-Z)")
    if not any(c.isdigit() for c in password):
        errors.append("dígitos (0 a 9)")
    if not any(not c.isalnum() for c in password):
        errors.append("especiais (!, $, #, %)")

    return errors


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
