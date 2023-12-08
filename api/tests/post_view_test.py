from django.test import TestCase
from rest_framework.test import APIClient
import json
from ..models import User, Post, Comment, PostAccess


class PostLocalViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.global_test_user = User.objects.create_user(
            username='global_test_user', password='123123')
        response = self.client.post('/api/login/', {
            "username": "global_test_user",
            "password": "123123"})
        self.token = json.loads(response.content)['token']
        self.global_public_post = Post.objects.create(
            id='17cbff5b-8737-4de7-b696-d169f57fd094',
            title='test post',
            contentType='text/plain',
            content='test content',
            visibility='PUBLIC',
            unlisted=False,
            author=self.global_test_user,
            source='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094',
            origin='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094',
        )
        self.global_comment = Comment.objects.create(
            id='17cbff5b-8737-4de7-b696-d169f57fd094',
            post=self.global_public_post,
            author=self.global_test_user,
            comment='test comment',
            published='2020-03-30T05:57:34.000Z',
        )

        self.global_private_post = Post.objects.create(
            id='ab9d66af-5cd1-4bd5-bdea-2e311f579542',
            title='test post',
            contentType='text/plain',
            content='test content',
            visibility='PRIVATE',
            unlisted=False,
            author=self.global_test_user,
            source='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/ab9d66af-5cd1-4bd5-bdea-2e311f579542',
            origin='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/ab9d66af-5cd1-4bd5-bdea-2e311f579542',
        )

    def test_get_post_list(self):
        response = self.client.get('/api/posts/')
        self.assertTrue(response.status_code >= 200 and response.status_code < 300)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data["items"]), 2)
        self.assertEqual(response_data["items"][0]["id"], 'ab9d66af-5cd1-4bd5-bdea-2e311f579542')
        self.assertEqual(response_data["items"][1]["id"], '17cbff5b-8737-4de7-b696-d169f57fd094')

    
    def test_get_post_detail(self):

        
