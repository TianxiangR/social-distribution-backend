from rest_framework import serializers
from api.models import User, Post, Comment, LikePost, LikeComment, Follow, InboxItem, FriendRequest
from urllib3.util import parse_url
import uuid
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

        
class PostSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Post
        fields = '__all__'

        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikePost
        fields = '__all__'


class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComment
        fields = '__all__'
 
        
class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'
        
        
class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboxItem
        fields = '__all__'
        

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'


class AuthorLocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'type', 'url', 'host', 'displayName', 'profileImage', 'github', 'is_following']

    type = serializers.SerializerMethodField()
    displayName = serializers.SerializerMethodField()
    profileImage = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        user = request.user
        return obj.followed_relations.filter(follower_id=user.id).exists()
    

    def get_type(self, obj):
        return 'author'


    def get_displayName(self, obj):
        return obj.username


    def get_profileImage(self, obj):
        request = self.context.get('request')
        if obj.is_foreign:
            return obj.image_url
        elif obj.profile_image:
            return f"{request.scheme}://{request.get_host()}/api/authors/{obj.id}/profile_image"
        
        return None
    
    
    def get_url(self, obj):
        if obj.is_foreign:
            return obj.url
        
        request = self.context.get('request')
        return f'{request.scheme}://{request.get_host()}/authors/{obj.id}'
    
    
    def get_host(self, obj):
        if obj.is_foreign:
            return parse_url(obj.url).host
        
        request = self.context.get('request')
        return f'{request.scheme}://{request.get_host()}/'

@extend_schema_serializer(examples=[
    OpenApiExample(
        name='author_detail',
        value={
            "id": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca",
            "type": "author",
            "url": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca",
            "host": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/",
            "displayName": "testaccount",
            "profileImage": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
            "github": "https://github.com/TianxiangR"
        }
    )
])
class AuthorRemoteSerializer(AuthorLocalSerializer):
    id = serializers.SerializerMethodField()
    
    def get_id(self, obj):
        request = self.context.get('request')
        return f'{request.scheme}://{request.get_host()}/authors/{obj.id}'


class AuthorListLocalSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    
    
    def get_type(self, obj):
        return 'authors'
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return AuthorLocalSerializer(obj, many=True, context={'request': request}).data
    
    
    def get_size(self, obj):
        return len(obj)
    
    
    def get_page(self, obj):
        return 1
    

@extend_schema_serializer(examples=[
    OpenApiExample(
        name='author_list',
        value={
            "type": "authors",
            "items": [
                {
                    "id": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                    "type": "author",
                    "url": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                    "host": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/",
                    "displayName": "testaccount",
                    "profileImage": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                    "github": "https://github.com/TianxiangR",
                },
                {
                    "id": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/2d144b1f-5ce0-4917-806d-23ca38170d67",
                    "type": "author",
                    "url": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/2d144b1f-5ce0-4917-806d-23ca38170d67",
                    "host": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/",
                    "displayName": "testaccount2",
                    "profileImage": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/api/authors/2d144b1f-5ce0-4917-806d-23ca38170d67/profile_image",
                    "github": None,
                },
                {
                    "id": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/592da35a-75a7-4507-a50d-e31c9e3718bd",
                    "type": "author",
                    "url": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/592da35a-75a7-4507-a50d-e31c9e3718bd",
                    "host": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/",
                    "displayName": "testaccount3",
                    "profileImage": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/api/authors/592da35a-75a7-4507-a50d-e31c9e3718bd/profile_image",
                    "github": None,
                }
            ],
            "size": 3,
            "page": 1
        }
    )
]) 
class AuthorListRemoteSerializer(AuthorListLocalSerializer):
    def get_items(self, obj):
        request = self.context.get('request')
        return AuthorRemoteSerializer(obj, many=True, context={'request': request}).data


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        

class CommentDetailRemoteSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    contentType = serializers.SerializerMethodField()
    published = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()


    def get_id(self, obj):
        request = self.context.get('request')
        return f'{request.scheme}://{request.get_host()}/authors/{obj.post.author.id}/posts/{obj.post.id}/comments/{obj.id}'
    
    
    def get_type(self, obj):
        return 'comment'
    
    
    def get_comment(self, obj):
        return obj.content
    
    
    def get_contentType(self, obj):
        return 'text/plain'
    
    
    def get_published(self, obj):
        # iso 8601 timestamp
        return obj.created_at.isoformat()
    
    
    def get_author(self, obj):
        request = self.context.get('request')
        return AuthorRemoteSerializer(obj.user, context={'request': request}).data
    
    
class CommentDetailLocalSerializer(CommentDetailRemoteSerializer):
    author = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    id = serializers.UUIDField()
    
    def get_author(self, obj):
        request = self.context.get('request')
        return AuthorLocalSerializer(obj.user, context={'request': request}).data
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        user = request.user
        return obj.likes.filter(user_id=user.id).exists()
    
    def get_like_count(self, obj):
        return obj.likes.count()


class PostBriefSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    title = serializers.CharField()
    id = serializers.UUIDField()
    origin = serializers.URLField()
    source = serializers.URLField()
    description = serializers.SerializerMethodField()
    contentType = serializers.CharField()
    content = serializers.CharField()
    author = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    published = serializers.SerializerMethodField()
    visibility = serializers.CharField()
    unlisted = serializers.BooleanField()
    content =   serializers.SerializerMethodField()


    def get_content(self, obj):
        if obj.contentType == "image":
            return ""
        return obj.content
    
    
    def get_type(self, obj):
        return 'post'
    
    
    def get_description(self, obj):
        return "This post is about " + obj.title
    
    
    def get_author(self, obj):
        request = self.context.get('request')
        return AuthorLocalSerializer(obj.author, context={'request': request}).data
    
    
    def get_categories(self, obj):
        return []
    
    
    def get_count(self, obj):
        return obj.comments.count()
    
    
    def get_published(self, obj):
        # iso 8601 timestamp
        return obj.created_at.isoformat()
    
    
    def get_comments(self, obj):
        request = self.context.get('request')
        return f"{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}/comments"
    

class PostBriefLocalSerializer(PostBriefSerializer):
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_my_post = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        user = request.user
        return obj.likes.filter(user_id=user.id).exists()
    
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    
    def get_is_my_post(self, obj):
        request = self.context.get('request')
        user = request.user
        return obj.author.id == user.id
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.contentType == "image":
            return f"{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}/image"
        
        return None
    



class PostDetailRemoteSerializer(PostBriefSerializer):
    commentsSrc = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    
    def get_id(self, obj):
        request = self.context.get('request')
        return f'{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}'
    
    def get_commentsSrc(self, obj):
        request = self.context.get('request')
        rval = {
            "type": "comments",
            "page": 1,
            "post": f"{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}",
            "id": f"{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}/comments",
            "comments": []
        }
        
        comments = obj.comments.all()
        for comment in comments:
            rval['comments'].append(CommentDetailRemoteSerializer(comment, context={'request': request}).data)
        rval["size"] = len(rval['comments'])
        
        return rval


class PostDetailLocalSerializer(PostBriefLocalSerializer):
    commentsSrc = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        user = request.user
        return obj.likes.filter(user_id=user.id).exists()
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_commentsSrc(self, obj):
        request = self.context.get('request')
        rval = {
            "type": "comments",
            "page": 1,
            "post": f"{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}",
            "id": f"{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}/comments",
            "comments": []
        }
        
        comments = obj.comments.all()
        for comment in comments:
            rval['comments'].append(CommentDetailLocalSerializer(comment, context={'request': request}).data)
        rval["size"] = len(rval['comments'])
        
        return rval
    

class PostBriefListSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    
    
    def get_type(self, obj):
        return 'posts'
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return PostBriefLocalSerializer(obj, many=True, context={'request': request}).data
    
    
    def get_size(self, obj):
        return len(obj)
    
    
    def get_page(self, obj):
        return 1

@extend_schema_serializer(examples=[
    OpenApiExample(
        name="post_list",
        value={
            "type": "posts",
            "items": [
                {
                    "type": "post",
                    "title": "a public post",
                    "id": "9cc05f7b-50e8-4d1a-b317-22ed57dd5a55",
                    "origin": "http://localhost:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/7caed011-4ae2-49f9-8a84-d745a73c366e",
                    "source": "http://localhost:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/7caed011-4ae2-49f9-8a84-d745a73c366e",
                    "description": "This post is about a public post",
                    "contentType": "text/plain",
                    "content": "a public post",
                    "author": {
                        "id": "465f0c29-690e-4960-96b4-98341eb29fca",
                        "type": "author",
                        "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                        "host": "http://127.0.0.1:8000/",
                        "displayName": "testaccount",
                        "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                        "github": "https://github.com/TianxiangR",
                    },
                    "categories": [],
                    "count": 0,
                    "comments": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/9cc05f7b-50e8-4d1a-b317-22ed57dd5a55/comments",
                    "published": "2023-11-27T21:09:21.334517+00:00",
                    "visibility": "PUBLIC",
                    "unlisted": False,
                    "commentsSrc": {
                        "type": "comments",
                        "page": 1,
                        "post": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/9cc05f7b-50e8-4d1a-b317-22ed57dd5a55",
                        "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/9cc05f7b-50e8-4d1a-b317-22ed57dd5a55/comments",
                        "comments": [],
                        "size": 0
                    }
                },
                {
                    "type": "post",
                    "title": "An image post",
                    "id": "9de8a419-b283-409e-bf0a-fc4c2f58de73",
                    "origin": "http://localhost:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/b6065868-6af5-4623-b64d-ed87f7ebf2a4",
                    "source": "http://localhost:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/b6065868-6af5-4623-b64d-ed87f7ebf2a4",
                    "description": "This post is about An image post",
                    "contentType": "image",
                    "content": "",
                    "author": {
                        "id": "465f0c29-690e-4960-96b4-98341eb29fca",
                        "type": "author",
                        "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                        "host": "http://127.0.0.1:8000/",
                        "displayName": "testaccount",
                        "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                        "github": "https://github.com/TianxiangR",
                    },
                    "categories": [],
                    "count": 0,
                    "comments": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/9de8a419-b283-409e-bf0a-fc4c2f58de73/comments",
                    "published": "2023-11-27T20:03:42.247025+00:00",
                    "visibility": "PUBLIC",
                    "unlisted": True,
                    "commentsSrc": {
                        "type": "comments",
                        "page": 1,
                        "post": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/9de8a419-b283-409e-bf0a-fc4c2f58de73",
                        "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/9de8a419-b283-409e-bf0a-fc4c2f58de73/comments",
                        "comments": [],
                        "size": 0
                    }
                },
                {
                    "type": "post",
                    "title": "This is a post",
                    "id": "1554101c-bfaa-474b-9491-7ae3b7142a76",
                    "origin": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/e1302863-f977-4d53-9d8c-c7621c14f6cd",
                    "source": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/e1302863-f977-4d53-9d8c-c7621c14f6cd",
                    "description": "This post is about This is a post",
                    "contentType": "text/plain",
                    "content": "some post",
                    "author": {
                        "id": "465f0c29-690e-4960-96b4-98341eb29fca",
                        "type": "author",
                        "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                        "host": "http://127.0.0.1:8000/",
                        "displayName": "testaccount",
                        "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                        "github": "https://github.com/TianxiangR",

                    },
                    "categories": [],
                    "count": 0,
                    "comments": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/1554101c-bfaa-474b-9491-7ae3b7142a76/comments",
                    "published": "2023-11-26T23:51:06.650538+00:00",
                    "visibility": "PUBLIC",
                    "unlisted": False,
                    "commentsSrc": {
                        "type": "comments",
                        "page": 1,
                        "post": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/1554101c-bfaa-474b-9491-7ae3b7142a76",
                        "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/1554101c-bfaa-474b-9491-7ae3b7142a76/comments",
                        "comments": [],
                        "size": 0
                    }
                },
                {
                    "type": "post",
                    "title": "This is a post",
                    "id": "17cbff5b-8737-4de7-b696-d169f57fd094",
                    "origin": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/3dcab3d9-c571-4ab0-831a-0d26288b413e",
                    "source": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/3dcab3d9-c571-4ab0-831a-0d26288b413e",
                    "description": "This post is about This is a post",
                    "contentType": "text/plain",
                    "content": "some post",
                    "author": {
                        "id": "465f0c29-690e-4960-96b4-98341eb29fca",
                        "type": "author",
                        "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                        "host": "http://127.0.0.1:8000/",
                        "displayName": "testaccount",
                        "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                        "github": "https://github.com/TianxiangR",
                    },
                    "categories": [],
                    "count": 9,
                    "comments": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments",
                    "published": "2023-11-26T23:30:53.965607+00:00",
                    "visibility": "PUBLIC",
                    "unlisted": False,
                    "commentsSrc": {
                        "type": "comments",
                        "page": 1,
                        "post": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094",
                        "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments",
                        "comments": [
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "leaving a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-26T23:43:41.724706+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/f83d2186-f873-45a7-a11b-4eef5d5c7a40"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "leaving a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-26T23:43:14.321041+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/a081ecda-2e00-47ff-8a86-e2293b6d23ea"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "leaving a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-26T23:38:56.139786+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/7315f185-e96e-492e-8f04-58eed536ffc1"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "leaving a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-26T23:36:43.884125+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/f40e9350-59ad-4e62-8e1a-f63d65b8400a"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "leaving a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-26T23:36:25.394946+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/2a0a0bb4-f943-4150-b857-5ebde4a581d1"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "leaving a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-26T23:36:04.208288+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/b316ac0c-837c-4501-a996-c22be45fe631"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "leaving a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-26T23:33:14.676910+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/a111defc-9d36-4464-826f-d2fe60dbdbda"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "leaving a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-26T23:31:51.423841+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/abbe7afc-76b3-4c7a-8c77-cb6b5ca88bdc"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "leaving a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-26T23:31:28.702346+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/17cbff5b-8737-4de7-b696-d169f57fd094/comments/0ead87fc-4649-4d72-b740-9db50ce8c05f"
                            }
                        ],
                        "size": 9
                    }
                },
                {
                    "type": "post",
                    "title": "This is a post",
                    "id": "8e7a3e7b-a833-42a1-b27b-f56561aa535a",
                    "origin": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/e4a9ddae-27c8-4811-8fb1-fc2891e4bb4a",
                    "source": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/e4a9ddae-27c8-4811-8fb1-fc2891e4bb4a",
                    "description": "This post is about This is a post",
                    "contentType": "text/plain",
                    "content": "some post",
                    "author": {
                        "id": "465f0c29-690e-4960-96b4-98341eb29fca",
                        "type": "author",
                        "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                        "host": "http://127.0.0.1:8000/",
                        "displayName": "testaccount",
                        "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                        "github": "https://github.com/TianxiangR",
                    },
                    "categories": [],
                    "count": 0,
                    "comments": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/8e7a3e7b-a833-42a1-b27b-f56561aa535a/comments",
                    "published": "2023-11-26T23:29:04.098010+00:00",
                    "visibility": "PUBLIC",
                    "unlisted": False,
                    "commentsSrc": {
                        "type": "comments",
                        "page": 1,
                        "post": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/8e7a3e7b-a833-42a1-b27b-f56561aa535a",
                        "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/8e7a3e7b-a833-42a1-b27b-f56561aa535a/comments",
                        "comments": [],
                        "size": 0
                    }
                },
                {
                    "type": "post",
                    "title": "This is a post",
                    "id": "16a0588a-2faf-4cd1-97a4-09e9bf1e854d",
                    "origin": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/e2680392-1289-4280-abbc-935d385addad",
                    "source": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/e2680392-1289-4280-abbc-935d385addad",
                    "description": "This post is about This is a post",
                    "contentType": "text/plain",
                    "content": "some post",
                    "author": {
                        "id": "465f0c29-690e-4960-96b4-98341eb29fca",
                        "type": "author",
                        "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                        "host": "http://127.0.0.1:8000/",
                        "displayName": "testaccount",
                        "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                        "github": "https://github.com/TianxiangR",
                    },
                    "categories": [],
                    "count": 0,
                    "comments": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/16a0588a-2faf-4cd1-97a4-09e9bf1e854d/comments",
                    "published": "2023-11-26T23:27:56.136825+00:00",
                    "visibility": "PUBLIC",
                    "unlisted": False,
                    "commentsSrc": {
                        "type": "comments",
                        "page": 1,
                        "post": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/16a0588a-2faf-4cd1-97a4-09e9bf1e854d",
                        "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/16a0588a-2faf-4cd1-97a4-09e9bf1e854d/comments",
                        "comments": [],
                        "size": 0
                    }
                },
                {
                    "type": "post",
                    "title": "This is a post",
                    "id": "34a5268f-8e7a-4830-bfa0-7babe4996cef",
                    "origin": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/789449f1-5072-4a90-83cd-82eb76ac4f83",
                    "source": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/789449f1-5072-4a90-83cd-82eb76ac4f83",
                    "description": "This post is about This is a post",
                    "contentType": "text/markdown",
                    "content": "# some post\n\nThis is a markdown post\n\n![image](http://localhost:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/9de8a419-b283-409e-bf0a-fc4c2f58de73/image)",
                    "author": {
                        "id": "465f0c29-690e-4960-96b4-98341eb29fca",
                        "type": "author",
                        "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                        "host": "http://127.0.0.1:8000/",
                        "displayName": "testaccount",
                        "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                        "github": "https://github.com/TianxiangR",
                    },
                    "categories": [],
                    "count": 0,
                    "comments": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/34a5268f-8e7a-4830-bfa0-7babe4996cef/comments",
                    "published": "2023-11-25T23:47:47.817792+00:00",
                    "visibility": "PUBLIC",
                    "unlisted": False,
                    "commentsSrc": {
                        "type": "comments",
                        "page": 1,
                        "post": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/34a5268f-8e7a-4830-bfa0-7babe4996cef",
                        "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/34a5268f-8e7a-4830-bfa0-7babe4996cef/comments",
                        "comments": [],
                        "size": 0
                    }
                },
                {
                    "type": "post",
                    "title": "This is a post",
                    "id": "b2900f92-6f16-4d47-9211-356e4ab43d24",
                    "origin": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/2229f519-d811-4102-a187-702d3aa648db",
                    "source": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/2229f519-d811-4102-a187-702d3aa648db",
                    "description": "This post is about This is a post",
                    "contentType": "text/plain",
                    "content": "some post",
                    "author": {
                        "id": "465f0c29-690e-4960-96b4-98341eb29fca",
                        "type": "author",
                        "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                        "host": "http://127.0.0.1:8000/",
                        "displayName": "testaccount",
                        "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                        "github": "https://github.com/TianxiangR",
                    },
                    "categories": [],
                    "count": 0,
                    "comments": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/b2900f92-6f16-4d47-9211-356e4ab43d24/comments",
                    "published": "2023-11-25T23:46:23.721858+00:00",
                    "visibility": "PUBLIC",
                    "unlisted": False,
                    "commentsSrc": {
                        "type": "comments",
                        "page": 1,
                        "post": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/b2900f92-6f16-4d47-9211-356e4ab43d24",
                        "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/b2900f92-6f16-4d47-9211-356e4ab43d24/comments",
                        "comments": [],
                        "size": 0
                    }
                },
                {
                    "type": "post",
                    "title": "This is a post",
                    "id": "4bb83515-9594-46b4-bab5-2f2d2b8865ca",
                    "origin": "http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/author/465f0c29-690e-4960-96b4-98341eb29fca/posts/22db380f-0816-4775-838c-ab93f75bf071",
                    "source": "http://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/author/465f0c29-690e-4960-96b4-98341eb29fca/posts/22db380f-0816-4775-838c-ab93f75bf071",
                    "description": "This post is about This is a post",
                    "contentType": "text/plain",
                    "content": "some post",
                    "author": {
                        "id": "465f0c29-690e-4960-96b4-98341eb29fca",
                        "type": "author",
                        "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                        "host": "http://127.0.0.1:8000/",
                        "displayName": "testaccount",
                        "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                        "github": "https://github.com/TianxiangR",
                    },
                    "categories": [],
                    "count": 4,
                    "comments": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/4bb83515-9594-46b4-bab5-2f2d2b8865ca/comments",
                    "published": "2023-11-23T21:48:39.211324+00:00",
                    "visibility": "PUBLIC",
                    "unlisted": False,
                    "commentsSrc": {
                        "type": "comments",
                        "page": 1,
                        "post": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/4bb83515-9594-46b4-bab5-2f2d2b8865ca",
                        "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/4bb83515-9594-46b4-bab5-2f2d2b8865ca/comments",
                        "comments": [
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "This is a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-23T21:51:09.492223+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/4bb83515-9594-46b4-bab5-2f2d2b8865ca/comments/b7f99d28-442c-47e6-895e-2d3fc79f6261"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "This is a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-23T21:51:07.740971+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/4bb83515-9594-46b4-bab5-2f2d2b8865ca/comments/8578a4de-f7b7-4e4f-9208-9c9c81502c11"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "This is a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-23T21:51:05.916920+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/4bb83515-9594-46b4-bab5-2f2d2b8865ca/comments/2e6e95c3-c248-476d-95e9-165ccb7d7fe0"
                            },
                            {
                                "type": "comment",
                                "author": {
                                    "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "type": "author",
                                    "url": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca",
                                    "host": "http://127.0.0.1:8000/",
                                    "displayName": "testaccount",
                                    "profileImage": "http://127.0.0.1:8000/api/authors/465f0c29-690e-4960-96b4-98341eb29fca/profile_image",
                                    "github": "https://github.com/TianxiangR",
                                },
                                "comment": "This is a comment",
                                "contentType": "text/plain",
                                "published": "2023-11-23T21:51:03.639980+00:00",
                                "id": "http://127.0.0.1:8000/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/4bb83515-9594-46b4-bab5-2f2d2b8865ca/comments/20b85287-616f-41c1-b2e7-de879cd56d94"
                            }
                        ],
                        "size": 4
                    }
                }
            ],
            "size": 9,
            "page": 1
        }
    )
])
class PostListSerializer(PostBriefListSerializer):
    items = serializers.SerializerMethodField()
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return PostDetailRemoteSerializer(obj, many=True, context={'request': request}).data
    

class CommentListRemoteSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    
    
    def get_type(self, obj):
        return 'comments'
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return CommentDetailRemoteSerializer(obj, many=True, context={'request': request}).data
    
    
    def get_size(self, obj):
        return len(obj)
    
    
    def get_page(self, obj):
        return 1
    
    
class CommentListLocalSerializer(CommentListRemoteSerializer):
    def get_items(self, obj):
        request = self.context.get('request')
        return CommentDetailLocalSerializer(obj, many=True, context={'request': request}).data
        
        
class FollowerListSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    
    
    def get_type(self, obj):
        return 'followers'
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return AuthorRemoteSerializer(obj, many=True, context={'request': request}).data
    
    
    def get_size(self, obj):
        return len(obj)
    
    
    def get_page(self, obj):
        return 1
    
    
class FriendRequestDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    requester = AuthorLocalSerializer()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    
    
class FriendRequestListSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    
    
    def get_type(self, obj):
        return 'friendrequests'
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return FriendRequestDetailSerializer(obj, many=True, context={'request': request}).data
    
    
    def get_size(self, obj):
        return len(obj)
    
    
    def get_page(self, obj):
        return 1
    


@extend_schema_serializer(examples=[
    OpenApiExample(
        name="Share Post Request",
        value={
            "type": "post",
            "title": "This is a post",
            "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
            "origin": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
            "source": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
            "description": "This post is about This is a post",
            "contentType": "text/plain",
            "content": "some post",
            "author": {
                "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "type": "author",
                "url": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host": "http://127.0.0.1:5454/",
                "displayName": "Lara Croft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "github": "http://github.com/laracroft"
            },
            "categories": [],
            "count": 4,
            "comments": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/5bb83515-9594-46b4-bab5-2f2d2b8865ca/comments",
            "commentsSrc": {
                "type": "comments",
                "page": 1,
                "post": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/5bb83515-9594-46b4-bab5-2f2d2b8865ca",
                "id": "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/465f0c29-690e-4960-96b4-98341eb29fca/posts/5bb83515-9594-46b4-bab5-2f2d2b8865ca/comments",
                "comments": [
                {
                    "type": "comment",
                    "author": {
                    "type": "author",
                    "id": "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                    "url": "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                    "host": "http://127.0.0.1:5454/",
                    "displayName": "Greg Johnsonn",
                    "github": "http://github.com/gjohnson",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                    },
                    "comment": "Sick Olde English",
                    "contentType": "text/markdown",
                    "published": "2023-11-27T15:06:49.623588+00:00",
                    "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c"
                }
                ],
                "size": 4
            },
            "published": "2023-11-23T21:48:39.211324+00:00",
            "visibility": "PRIVATE",
            "unlisted": False
            }
    ),
    OpenApiExample(
        name="Follow Request",
        value={
            "type": "Follow",      
            "summary":"Greg wants to follow Lara",
            "actor":{
                "type":"author",
                "id":"http://127.0.0.1:5454/authors/057aa887-40a9-4c09-be96-10bb36343d0a",
                "url":"http://127.0.0.1:5454/authors/057aa887-40a9-4c09-be96-10bb36343d0a",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Greg Johnson",
                "github": "http://github.com/gjohnson",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "object":{
                "type":"author",
                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Lara Croft",
                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "github": "http://github.com/laracroft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            }
        }
    )
])
class InboxRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboxItem
        fields = '__all__'