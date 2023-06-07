from django.shortcuts import render, redirect
from django.views import View


def index(request):
    return redirect("password")


class PasswordView(View):
    def get(self, request):
        template_name = "password.html"
        return render(request, template_name)
