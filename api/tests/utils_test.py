from django.test import TestCase
from ..utils import is_uuid, is_comment_detail_url, is_post_detail_url, get_post_id_from_url, get_author_id_from_url, get_comment_id_from_url, get_or_create_user, has_access_to_post
from rest_framework.exceptions import ParseError
from ..models import User, Post, Comment, PostAccess

class UtilsTest(TestCase):

    def test_is_uuid(self):
        self.assertTrue(is_uuid('123e4567-e89b-12d3-a456-426655440000'))
        self.assertFalse(is_uuid('123e4567-e89b-12d3-a456-42665544000'))

    
    def test_is_comment_detail_url(self):
        self.assertTrue(is_comment_detail_url('http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/f83d2186-f873-45a7-a11b-4eef5d5c7a40'))
        self.assertFalse(is_comment_detail_url('http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/'))
        self.assertTrue(is_comment_detail_url('http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29690e496096b498341eb29fca/posts/17cbff5b87374de7b696d169f57fd094/comments/f83d2186f87345a7a11b4eef5d5c7a40'))


    def test_is_post_detail_url(self):
        self.assertTrue(is_post_detail_url('http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094'))
        self.assertFalse(is_post_detail_url('http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/'))
        self.assertTrue(is_post_detail_url('http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29690e496096b498341eb29fca/posts/17cbff5b87374de7b696d169f57fd094'))

    
    def test_get_post_id_from_url(self):
        self.assertEqual(get_post_id_from_url('http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094'), '17cbff5b-8737-4de7-b696-d169f57fd094')
        self.assertEqual(get_post_id_from_url(
            'http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29690e496096b498341eb29fca/posts/17cbff5b87374de7b696d169f57fd094'), '17cbff5b-8737-4de7-b696-d169f57fd094')
        self.assertRaises(ParseError, get_post_id_from_url, 'http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29690e496096b498341eb29fca/posts/')


    def test_get_author_id_from_url(self):
        self.assertEqual(get_author_id_from_url('http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca'), '465f0c29-690e-4960-96b4-98341eb29fca')
        self.assertEqual(get_author_id_from_url(
            'http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29690e496096b498341eb29fca'), '465f0c29-690e-4960-96b4-98341eb29fca')
        self.assertRaises(ParseError, get_author_id_from_url, 'http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/')
        
    
    def test_get_comment_id_from_url(self):
        self.assertEqual(get_comment_id_from_url('http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/f83d2186-f873-45a7-a11b-4eef5d5c7a40'), 'f83d2186-f873-45a7-a11b-4eef5d5c7a40')
        self.assertEqual(get_comment_id_from_url(
            'http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29690e496096b498341eb29fca/posts/17cbff5b87374de7b696d169f57fd094/comments/f83d2186f87345a7a11b4eef5d5c7a40'), 'f83d2186-f873-45a7-a11b-4eef5d5c7a40')
        self.assertRaises(ParseError, get_comment_id_from_url, 'http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29690e496096b498341eb29fca/posts/17cbff5b87374de7b696d169f57fd094/comments/')


    def test_get_or_create_user(self):
        obj = {
            "id": "http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca",
            "host": "http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/",
            "displayName": "Tian",
            "url": "http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca",
            "github": "https://github.com/TianxiangR",
            "profileImage": "https://avatars.githubusercontent.com/u/43115521?v=4"
        }

        user = get_or_create_user(obj)
        self.assertEqual(user.id, '465f0c29-690e-4960-96b4-98341eb29fca')
        self.assertEqual(user.host, 'http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/')
        self.assertEqual(user.displayName, 'Tian')


    def test_has_access_to_post(self):
        author_obj = User.objects.create(
            id='465f0c29-690e-4960-96b4-98341eb29fca',
            username='TianxiangR',
            displayName='Tian',
            host='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/',
        )

        public_post_obj = Post.objects.create(
            id='17cbff5b-8737-4de7-b696-d169f57fd094',
            title='test post',
            contentType='text/plain',
            content='test content',
            visibility='PUBLIC',
            unlisted=False,
            author=author_obj,
            source='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094',
            origin='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094',
        )

        another_user = User.objects.create(
            id='a28f3360-31ae-4228-87a4-f33531794980',
            username='testaccount',
            displayName='testaccount',
            host='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/',
        )
        self.assertTrue(has_access_to_post(public_post_obj, author_obj))
        self.assertTrue(has_access_to_post(public_post_obj, another_user))

        private_post_obj = Post.objects.create(
            id='ab9d66af-5cd1-4bd5-bdea-2e311f579542',
            title='test post',
            contentType='text/plain',
            content='test content',
            visibility='PRIVATE',
            unlisted=False,
            author=author_obj,
            source='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094',
            origin='http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094',
        )

        self.assertTrue(has_access_to_post(private_post_obj, author_obj))
        self.assertFalse(has_access_to_post(private_post_obj, another_user))

        PostAccess.objects.create(post=private_post_obj, user=another_user)

        self.assertTrue(has_access_to_post(private_post_obj, another_user))



        


