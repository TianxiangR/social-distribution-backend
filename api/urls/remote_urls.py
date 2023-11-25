from django.urls import path

from ..views import authors, posts, comments, followers, inbox

urlpatterns = [
    # cross site apis
    path('authors/', authors.AuthorListRemote.as_view() , name='author-list'),
    path('authors/<uuid:author_id>', authors.AuthorDetail.as_view(), name='author-detail'),
    path('authors/<uuid:author_id>/posts/', posts.PostListRemote.as_view(), name='post-list'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>', posts.PostDetailRemote.as_view(), name='post-detail'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments', comments.CommentListRemote.as_view(), name='comment-list'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>', comments.CommentDetailRemote.as_view(), name='comment-detail'),
    path('authors/<uuid:author_id>/followers', followers.FollowerListRemote.as_view(), name='follower-list'),
    path('authors/<uuid:author_id>/inbox', inbox.InboxListRemote.as_view(), name='inbox-list'),
]