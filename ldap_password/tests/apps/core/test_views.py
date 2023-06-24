from django.test import TestCase, Client
from django.urls import reverse


class IndexViewTestCase(TestCase):
    def __init__(self, methodName: str = "IndexView") -> None:
        self.client = Client()
        self.url = reverse("index")
        super().__init__(methodName)

    def test_redirect_to_password_page(self):
        response = self.client.get(self.url)
        expected_url = reverse("password")
        self.assertRedirects(response, expected_url, status_code=302)


class PasswordViewTestCase(TestCase):
    def __init__(self, methodName: str = "RequestMailView") -> None:
        self.client = Client()
        self.url = reverse("password")
        super().__init__(methodName)

    def test_should_return_password_page_status_200(self):
        template_name = "password.html"
        enterprise_name_attribute = "enterprise_name"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsInstance(response.context[enterprise_name_attribute], str)

    def test_should_return_template_invalid_form_data(self):
        template_name = "password.html"
        enterprise_name_attribute = "enterprise_name"
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsInstance(response.context[enterprise_name_attribute], str)
        self.assertIsNone(response.context["username"])
        self.assertIsNone(response.context["current_password"])
        self.assertIsNone(response.context["new_password"])
        self.assertIsNone(response.context["repeate_password"])

    def test_should_return_template_invalid_form_data_with_username(self):
        template_name = "password.html"
        enterprise_name_attribute = "enterprise_name"
        response = self.client.post(self.url, data={"username": "username"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsInstance(response.context[enterprise_name_attribute], str)
        self.assertEqual(response.context["username"], "username")
        self.assertIsNone(response.context["current_password"])
        self.assertIsNone(response.context["new_password"])
        self.assertIsNone(response.context["repeate_password"])

    def test_should_return_template_invalid_form_different_passwords(self):
        template_name = "password.html"
        enterprise_name_attribute = "enterprise_name"
        data = {
            "username": "username",
            "current_password": "abc",
            "new_password": "abcd",
            "repeate_password": "abcde",
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsInstance(response.context[enterprise_name_attribute], str)
        self.assertEqual(response.context["username"], "username")
        self.assertEqual(response.context["current_password"], "abc")
        self.assertEqual(response.context["new_password"], "abcd")
        self.assertEqual(response.context["repeate_password"], "abcde")

    def test_should_redirect_to_password_valid_form(self):
        data = {
            "username": "username",
            "current_password": "abc",
            "new_password": "abcd",
            "repeate_password": "abcd",
        }
        response = self.client.post(self.url, data=data)
        expected_url = reverse("password")
        self.assertRedirects(response, expected_url, status_code=302)


class RequestMailViewTestCase(TestCase):
    def __init__(self, methodName: str = "RequestMailView") -> None:
        self.client = Client()
        self.url = reverse("mail")
        super().__init__(methodName)

    def test_should_return_mail_page_status_200(self):
        template_name = "mail.html"
        enterprise_name_attribute = "enterprise_name"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsInstance(response.context[enterprise_name_attribute], str)

    def test_should_return_template_invalid_form_username(self):
        template_name = "mail.html"
        enterprise_name_attribute = "enterprise_name"
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsInstance(response.context[enterprise_name_attribute], str)

    def test_should_redirect_valid_username(self):
        response = self.client.post(self.url, data={"username": "pedro"})
        expected_url = reverse("mail")
        self.assertRedirects(response, expected_url, status_code=302)


class ConfirmTokenViewTestCase(TestCase):
    def __init__(self, methodName: str = "ConfirmTokenView") -> None:
        self.client = Client()
        self.url = reverse("token")
        super().__init__(methodName)

    def test_redirect_to_mail_page(self):
        response = self.client.get(self.url)
        expected_url = reverse("mail")
        self.assertRedirects(response, expected_url, status_code=302)

    def test_should_return_token_page_status_200(self):
        template_name = "token.html"
        enterprise_name_attribute = "enterprise_name"
        username_attribute = "username"
        session = self.client.session
        session[username_attribute] = username_attribute
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsInstance(response.context[enterprise_name_attribute], str)
        self.assertIsInstance(response.context[username_attribute], str)
        self.assertEqual(response.context[username_attribute], "username")

    def test_should_return_template_invalid_token(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 302)

    def test_should_return_template_invalid_username(self):
        session = self.client.session
        session["token"] = "valid_token"
        session["username"] = "username"
        session.save()
        data = {"token": "valid_token"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
