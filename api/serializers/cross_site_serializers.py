from rest_framework import serializers
from ..models import User, Post, Comment, LikePost, LikeComment, Follow, PostAccessPermission, Notification, Inbox
from ..utils import has_access_to_comment

class AuthorSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'type', 'url', 'host', 'displayName', 'profileImage']
    
  type = serializers.SerializerMethodField()
  url = serializers.SerializerMethodField()
  host = serializers.SerializerMethodField()
  displayName = serializers.SerializerMethodField()
  profileImage = serializers.SerializerMethodField()
  id = serializers.SerializerMethodField()
  
  def get_id(self, obj):
    request = self.context.get('request')
    return request.build_absolute_uri(str(obj.id))

  
  def get_type(self, obj):
    return 'author'
  
  
  def get_url(self, obj):
    request = self.context.get('request')
    return request.build_absolute_uri(str(obj.id))
  
  
  def get_host(self, obj):
    request = self.context.get('request')
    return 'http://' + request.get_host() + '/'
  
  
  def get_displayName(self, obj):
    return obj.username
  
  
  def get_profileImage(self, obj):
    request = self.context.get('request')
    if obj.profile_image:
      img_url = obj.profile_image.url
    else:
      return None
    return request.build_absolute_uri(img_url)
  
  
class CommentSerializer(serializers.Serializer):
  type = serializers.SerializerMethodField()
  author = serializers.SerializerMethodField()
  comment = serializers.SerializerMethodField()
  contentType = serializers.SerializerMethodField()
  published = serializers.SerializerMethodField()
  id = serializers.SerializerMethodField()
  
  def get_type(self, obj):
    return 'comment'
  
  def get_comment(self, obj):
    return obj.content
  
  def get_contentType(self, obj):
    return 'text/plain'
  
  def get_id(self, obj):
    return str(obj.post.origin) + '/comments/' + str(obj.id)
  
  def get_published(self, obj):
    return obj.created_at.isoformat()
  
  def get_author(self, obj):
    request = self.context.get('request')
    return AuthorSerializer(obj.user, context={'request': request}).data
  
  
class PostSerializer(serializers.ModelSerializer):
  comments = serializers.SerializerMethodField()
  count = serializers.SerializerMethodField()
  author = AuthorSerializer()
  published = serializers.SerializerMethodField()
  id = serializers.SerializerMethodField()
  description = serializers.SerializerMethodField()
  
  class Meta:
    model = Post
    fields = ['id', 'title', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'count', 'comments', 'published', 'visibility', 'unlisted', 'source', 'origin']

  
  def get_id(self, obj):
    request = self.context.get('request')
    return obj.origin

  
  def get_comments(self, obj):
    return str(obj.origin) + '/comments'

  
  def get_count(self, obj):
    return obj.comments.count()

  
  def get_published(self, obj):
    # iso 8601 timestamp
    return obj.created_at.isoformat()

  
  def get_description(self, obj):
    return "There is no description for this post."


class InboxSerializer(serializers.ModelSerializer):
  class Meta:
    model = Inbox
    fields = '__all__'

  
  

