
from rest_framework.generics import GenericAPIView, get_object_or_404
from ..models import User, Post, Comment, LikePost, LikeComment
from ..serializers.cross_site_serializers import AuthorSerializer, PostSerializer, CommentSerializer, InboxSerializer
from ..serializers.insite_serializers import LikePostSerializer, LikeCommentSerializer, FollowSerializer, PostAccessPermissionSerializer, CommentSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView,get_object_or_404
from rest_framework import status
from drf_spectacular.utils import extend_schema
from dateutil.parser import parse
from ..utils import get_foreign_author_or_create

class Liked(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, **kwargs):
        host_name = request.get_host()
        
        user = Token.objects.get(key=request.auth).user
        posts = LikePost.objects.filter(user=user)
        comments = LikeComment.objects.filter(user=user)
        liked_items = []
        for post in posts:
            liked_items.append({
                "@context": "https://www.w3.org/ns/activitystreams",
                    "summary": f"{user.username} liked your post",
                    "type": "Like",
                    "author": {
                        "id": f"http://{host_name}/authors/{user.id}",
                        "type": "author",
                        "url": f"http://{host_name}/authors/{user.id}",
                        "host": f"http://{host_name}",
                        "displayName": f"{user.username}",
                        "profileImage": f"http://{host_name}/media/{user.profile_image}"
                    },
                    "object": f"http://{host_name}/authors/{user.id}/posts/{post.id}"
            })
            
        for comment in comments:
            liked_items.append({
                "@context": "https://www.w3.org/ns/activitystreams",
                    "summary": f"{user.username} liked your comment",
                    "type": "Like",
                    "author": {
                        "id": f"http://{host_name}/authors/{user.id}",
                        "type": "author",
                        "url": f"http://{host_name}/authors/{user.id}",
                        "host": f"http://{host_name}",
                        "displayName": f"{user.username}",
                        "profileImage": f"http://{host_name}/media/{user.profile_image}"
                    },
                    "object": f"http://{host_name}/authors/{user.id}/posts/{post.id}/comments/{comment.id}"
            })

        response_body = {
            "type": "liked",
            "items": liked_items
        }
        return Response(response_body, status=status.HTTP_200_OK)