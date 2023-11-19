from django.contrib import admin
from django.urls import path

from ..views import cross_site

urlpatterns = [
    # cross site apis
    path('authors/', cross_site.AuthorList.as_view(), name='authors'),
    path('authors/<uuid:author_id>', cross_site.AuthorDetail.as_view(), name='author_detail'),
    path('authors/<uuid:author_id>/followers', cross_site.FollowerList.as_view(), name='author_followers'),
    path('authors/<uuid:author_id>/posts/', cross_site.AuthorPostList.as_view(), name='author_posts'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>', cross_site.AuthorPostDetail.as_view(), name='author_post_detail'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments', cross_site.AuthorPostCommentList.as_view(), name='author_post_comments'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/inbox', cross_site.AuthorInboxList.as_view(), name='author_post_inbox'),
]