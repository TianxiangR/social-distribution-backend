from django.contrib import admin
from django.urls import path

from ..views import follows, users, posts, comments, notifications, cross_site

urlpatterns = [
    # insite apis
    path('login/', users.signin, name='login'),
    path('signup/', users.signup, name='signup'),
    path('update_password/<uuid:pk>', users.update_password, name='update_password'),
    path('get_likes_for_user/<int:pk>', users.get_likes_for_user, name='get_likes_for_user'),

    path('posts/', posts.PostList.as_view(), name='authors'),
    path('posts/<uuid:post_id>', posts.PostDetail.as_view(), name='post_detail'),
    path('posts/<uuid:post_id>/likes', posts.PostLikeList.as_view(), name='post_like'),
    path('posts/<uuid:post_id>/comments/', comments.CommentList.as_view(), name='comments'),
    path('posts/<uuid:post_id>/comments/<uuid:comment_id>', comments.CommentDetail.as_view(), name='comments'),
    path('posts/<uuid:post_id>/comments/<uuid:comment_id>/likes', comments.LikeCommentList.as_view(), name='comments'),
    path('authors', users.UserList.as_view(), name='authors'),
    path('authors/<int:author_id>/posts/', users.UserDetail.as_view(), name='authors'),
    
    path('follows', follows.FollowList.as_view(), name='follows'),
    
    path('notifications', notifications.NotificationList.as_view(), name='notifications'),
    path('notifications/<uuid:notification_id>', notifications.NotificationDetail.as_view(), name='notifications'),
]