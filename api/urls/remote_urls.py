from django.urls import path

from ..views import authors, posts, comments, follows, inbox, likes, image

urlpatterns = [
    # cross site apis
    path('authors/', authors.AuthorListRemote.as_view() , name='author-list'),
    path('authors/<uuid:author_id>', authors.AuthorDetailRemote.as_view(), name='author-detail'),
    path('authors/<uuid:author_id>/posts/', posts.PostListRemote.as_view(), name='post-list'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>', posts.PostDetailRemote.as_view(), name='post-detail'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments', comments.CommentListRemote.as_view(), name='comment-list'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>', comments.CommentDetailRemote.as_view(), name='comment-detail'),
    path('authors/<uuid:author_id>/followers', follows.FollowerListRemote.as_view(), name='follower-list'),
    path('authors/<uuid:author_id>/followers/<uuid:foreign_id>', follows.FollowDetailRemote.as_view(), name='follower-detail'),
    path('authors/<uuid:author_id>/inbox', inbox.InboxListRemote.as_view(), name='inbox-list'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/likes', likes.LikePostListRemote.as_view(), name='like-post-list'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/likes', likes.LikeCommentListRemote.as_view(), name='like-comment-list'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/image', image.PostImage.as_view(), name='post-image'),
]