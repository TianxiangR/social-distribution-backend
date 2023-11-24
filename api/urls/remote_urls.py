from django.urls import path

from ..views.remote import authors

urlpatterns = [
    # cross site apis
    path('authors/', authors.AuthorList.as_view(), name='authors'),
    path('authors/<uuid:author_id>/', authors.AuthorDetail.as_view(), name='author_detail'),
    path('authors/<uuid:author_id>/followers', authors.AuthorFollowList.as_view(), name='author_followers'),
    path('authors/<uuid:author_id>/followers/<str:foreign_author_id>', authors.AuthorFollowDetail.as_view(), name='author_follow_detail'),
    path('authors/<uuid:author_id>/posts/', authors.AuthorPostList.as_view(), name='author_posts'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>', authors.AuthorPostDetail.as_view(), name='author_post_detail'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments', authors.AuthorPostCommentList.as_view(), name='author_post_comments'),
    path('authors/<uuid:author_id>/inbox', authors.AuthorInboxList.as_view(), name='author_post_inbox'),
]