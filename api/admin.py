from django.contrib import admin
from .models import User, Post, Follow, Comment, LikePost, LikeComment, InboxItem, FriendRequest, PostAccess

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(LikePost)
admin.site.register(LikeComment)
admin.site.register(InboxItem)
admin.site.register(FriendRequest)
admin.site.register(PostAccess)