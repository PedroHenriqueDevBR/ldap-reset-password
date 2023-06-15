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
