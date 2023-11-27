from rest_framework import serializers
from api.models import User, Post, Comment, LikePost, LikeComment, Follow, InboxItem, FriendRequest
from urllib3.util import parse_url
import uuid


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
    content = serializers.SerializerMethodField()
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
    
    def get_content(self, obj):
        if obj.contentType == "image":
            return ""
        return obj.content
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.contentType == "image":
            return f"{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}/image"
        
        return None
    



class PostDetailRemoteSerializer(PostBriefSerializer):
    commentsSrc = serializers.SerializerMethodField()
    
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