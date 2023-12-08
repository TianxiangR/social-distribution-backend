from django.test import TestCase
from rest_framework.test import APIClient
import json
from ..models import User

class UserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(username='global_test_user', password='123123')


    def test_signup(self):
        response = self.client.post('/api/signup/', {
            "username": "test",
            "password": "test"})
        self.assertTrue(response.status_code >= 200 and response.status_code < 300)
        self.assertTrue(User.objects.filter(username='test').exists())

    
    def test_login(self):
        response = self.client.post('/api/login/', {
            "username": "global_test_user",
            "password": "123123"})
        self.assertTrue(response.status_code >= 200 and response.status_code < 300)

    
