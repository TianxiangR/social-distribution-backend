from rest_framework.permissions import BasePermission, SAFE_METHODS
from api.utils import has_access_to_post

class IsPostOwnerOrReadOnly(BasePermission):
    message = 'You do not have access to this post'
    code = 'no_access_to_post'
  
    def has_object_permission(self, request, view, obj):
        # allow GET requests to posts that the user has access to
        if request.method in SAFE_METHODS:
            return has_access_to_post(request.user, obj) or obj.author == request.user
        # only allow POST, PUT, PATCH, DELETE requests to posts that the user owns
        return obj.author == request.user
    

class IsPostModifyPermissionOwner(BasePermission):
    message = 'You do not permission to change this post'
    code = 'no_permission_to_change_post'
  
    def has_object_permission(self, request, view, obj):
        print("obj.author: ", obj.author)
        return has_access_to_post(request.user, obj) or obj.author == request.user
    

class IsCommentOwnerOrReadOnly(BasePermission):
    message = 'You do not have access to this comment'
    code = 'no_access_to_comment'
  
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            # only the comment author and the post author can access the comment on non-public posts
            if obj.post.visibility == 'public':
                return True
            return obj.post.author == request.user or obj.user == request.user
        # only the comment author can edit the comment
        return obj.user == request.user


class IsCommentModifyPermissionOwner(BasePermission):
    message = 'You do not have access to this comment'
    code = 'no_access_to_comment'
    
    def has_object_permission(self, request, view, obj):
        if obj.post.visibility == 'public':
                return True
        return obj.post.author == request.user or obj.user == request.user

class IsServer(BasePermission):
    message = 'You do not have access to this comment'
    code = 'no_access_to_comment'
    
    def has_permission(self, request, view):
        return request.user.is_server

