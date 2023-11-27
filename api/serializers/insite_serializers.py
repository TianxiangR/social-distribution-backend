from rest_framework import serializers
from ..models import User, Post, Comment, LikePost, LikeComment, Follow, PostAccessPermission, Notification
from ..utils import has_access_to_comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image', 'created_at']
    
    # correct way to hash password: https://stackoverflow.com/questions/49189484/how-to-mention-password-field-in-serializer
    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(self.initial_data['password'])
        user.save()
        return user
    
    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        try:
            user.set_password(self.initial_data['password'])
            user.save()
        except KeyError:
            pass
        return user
    
class UserInfoSerializer(UserSerializer):
    profile_image = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image', 'created_at', 'is_following']
    
    def get_profile_image(self, obj):
        request = self.context.get('request')
        try:
            img_url = obj.profile_image.url
            return request.build_absolute_uri(img_url)
        except ValueError:
            return None
        
    def get_is_following(self, obj):
        request = self.context.get('request')
        user = request.user
        if user:
            return obj.follower_relations.filter(follower=user).exists()
        return False
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        
class PostListItemSerializer(PostSerializer):
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    author_profile_image = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_my_post = serializers.SerializerMethodField()
    allowed_users = serializers.SerializerMethodField()
    
    def get_like_count(self, obj) -> int:
        return obj.likes.count()
    
    def get_comment_count(self, obj) -> int:
        counter = 0
        request = self.context.get('request')
        for comment in obj.comments.all():
            if has_access_to_comment(request.user, comment):
                counter += 1
        return counter
        
    def get_author_profile_image(self, obj) -> str:
        request = self.context.get('request')
        try:
            img_url = obj.author.profile_image.url
            
            if not img_url:
                return None
            
            # source: https://stackoverflow.com/questions/35522768/django-serializer-imagefield-to-get-full-url
            return request.build_absolute_uri(img_url)
        except ValueError:
            return None
        
    def get_author_name(self, obj) -> str:
        return obj.author.username
    
    def get_is_liked(self, obj) -> bool:
        request = self.context.get('request')
        user = request.user
        if user:
            return obj.likes.filter(user=user).exists()
        return False
    
    def get_is_my_post(self, obj) -> bool:
        request = self.context.get('request')
        user = request.user
        if user:
            return obj.author == user
        return False
    
    def get_allowed_users(self, obj) -> list[str]:
        request = self.context.get('request')
        user = request.user
        if user:
            access_permissions = obj.post_access_permissions.all()
            return [str(access_permission.user.id) for access_permission in access_permissions]
        return []
    
class PostDetailSerializer(PostListItemSerializer):
    comments = serializers.SerializerMethodField()
    is_my_post = serializers.SerializerMethodField()
        
    def get_comments(self, obj) -> list[dict]:
        comments = obj.comments.all()
        accessible_comments = [comment for comment in comments if has_access_to_comment(self.context.get('request').user, comment)]
        context = self.context
        return CommentDetailSerializer(accessible_comments, many=True, context=context).data
    
    def get_is_my_post(self, obj) -> bool:
        request = self.context.get('request')
        if request is None:
            return None
        user = request.user
        if user:
            return obj.author == user
        return False

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        
class CommentDetailSerializer(CommentSerializer):
    like_count = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    user_profile_image = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_my_comment = serializers.SerializerMethodField()
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_user_profile_image(self, obj):
        request = self.context.get('request')
        if obj.user.profile_image:
            img_url = obj.user.profile_image.url
        else:
            img_url = ''
        return request.build_absolute_uri(img_url)
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        user = request.user
        
        if user:
            return obj.likes.filter(user=user).exists()
        return False
    
    def get_is_my_comment(self, obj):
        request = self.context.get('request')
        user = request.user
        if user:
            return obj.user == user
        return False
    
        
class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikePost
        fields = '__all__'

class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComment
        fields = '__all__'
        
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

class PostAccessPermissionSerializer(serializers.ModelSerializer):
    author_follow_relation = serializers.SerializerMethodField()
    target_follow_relation = serializers.SerializerMethodField()
    
    class Meta:
        model = PostAccessPermission
        fields = '__all__'
        
class NotificationSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Notification
        fields = '__all__'
        
class NotificationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user_id', 'author_id', 'post_id', 'type', 'created_at', 'author_profile_image', 'author_username', 'post_title', 'comment_id', 'comment_content', 'is_read'] 
    
    
    user_id = serializers.SerializerMethodField()
    author_id = serializers.SerializerMethodField()
    post_id = serializers.SerializerMethodField()
    author_profile_image = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()
    post_title = serializers.SerializerMethodField()
    comment_id = serializers.SerializerMethodField()
    comment_content = serializers.SerializerMethodField()
    
    def get_user_id(self, obj):
        return obj.user.id
    
    
    def get_author_id(self, obj):
        return obj.author.id
    
    
    def get_post_id(self, obj):
        return obj.post.id
    
    
    def get_author_profile_image(self, obj):
        request = self.context.get('request')
        if obj.author.profile_image:
            img_url = obj.author.profile_image.url
        else:
            return None
        return request.build_absolute_uri(img_url)
    
    
    def get_author_username(self, obj):
        return obj.author.username
    
    
    def get_post_title(self, obj):
        return obj.post.title
    
    
    def get_comment_id(self, obj):
        if obj.comment is None:
            return None
        
        return obj.comment.id
    
    
    def get_comment_content(self, obj):
        if obj.comment is None:
            return None
        
        return obj.comment.content