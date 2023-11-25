from rest_framework import serializers
from api.models import User, Post, Comment, LikePost, LikeComment, Follower, InboxItem, FriendRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        
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
        model = Follower
        fields = '__all__'
        
        
class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboxItem
        fields = '__all__'
        

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'
        

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'type', 'url', 'host', 'displayName', 'profileImage', 'github']

    type = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    displayName = serializers.SerializerMethodField()
    profileImage = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()


    def get_id(self, obj):
        request = self.context.get('request')
        return f"{request.scheme}://{request.get_host()}/authors/{obj.id}"


    def get_type(self, obj):
        return 'author'


    def get_url(self, obj):
        return self.get_id(obj)


    def get_host(self, obj):
        request = self.context.get('request')
        return 'http://' + request.get_host() + '/'


    def get_displayName(self, obj):
        return obj.username


    def get_profileImage(self, obj):
        request = self.context.get('request')
        if obj.is_foreign:
            return obj.image_url
        elif obj.profile_image and obj.profile_image.url:
            return request.build_absolute_uri(obj.profile_image.url)
        
        return None


class AuthorListSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    
    
    def get_type(self, obj):
        return 'authors'
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return AuthorSerializer(obj, many=True, context={'request': request}).data
    
    
    def get_size(self, obj):
        return len(obj)
    
    
    def get_page(self, obj):
        return 1


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        

class CommentDetailSerializer(serializers.Serializer):
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
        return AuthorSerializer(obj.user, context={'request': request}).data


class PostDetailSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    title = serializers.CharField()
    id = serializers.SerializerMethodField()
    origin = serializers.URLField()
    source = serializers.URLField()
    description = serializers.SerializerMethodField()
    contentType = serializers.CharField()
    content = serializers.CharField()
    author = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    commentsSrc = serializers.SerializerMethodField()
    published = serializers.SerializerMethodField()
    visibility = serializers.CharField()
    unlisted = serializers.BooleanField()
    
    
    def get_type(self, obj):
        return 'post'
    
    
    def get_id(self, obj):
        request = self.context.get('request')
        return f'{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}'
    
    
    def get_description(self, obj):
        return "This post is about " + obj.title
    
    
    def get_author(self, obj):
        request = self.context.get('request')
        return AuthorSerializer(obj.author, context={'request': request}).data
    
    
    def get_categories(self, obj):
        return []
    
    
    def get_count(self, obj):
        return obj.comments.count()
    
    
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
            rval['comments'].append(CommentDetailSerializer(comment, context={'request': request}).data)
        rval["size"] = len(rval['comments'])
        
        return rval
    
    
    def get_published(self, obj):
        # iso 8601 timestamp
        return obj.created_at.isoformat()
    
    
    def get_comments(self, obj):
        request = self.context.get('request')
        return f"{request.scheme}://{request.get_host()}/authors/{obj.author.id}/posts/{obj.id}/comments"
    

class PostListSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    
    
    def get_type(self, obj):
        return 'posts'
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return PostDetailSerializer(obj, many=True, context={'request': request}).data
    
    
    def get_size(self, obj):
        return len(obj)
    
    
    def get_page(self, obj):
        return 1


class CommentListSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    
    
    def get_type(self, obj):
        return 'comments'
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return CommentDetailSerializer(obj, many=True, context={'request': request}).data
    
    
    def get_size(self, obj):
        return len(obj)
    
    
    def get_page(self, obj):
        return 1
        
        
class FollowerListSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    
    
    def get_type(self, obj):
        return 'followers'
    
    
    def get_items(self, obj):
        request = self.context.get('request')
        return AuthorSerializer(obj, many=True, context={'request': request}).data
    
    
    def get_size(self, obj):
        return len(obj)
    
    
    def get_page(self, obj):
        return 1