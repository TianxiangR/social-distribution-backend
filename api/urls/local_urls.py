from django.urls import path

from ..views import users, authors, posts, comments, likes, follows,friend_request, image

urlpatterns = [
    # insite apis
    path('login/', users.signin, name='login'),
    path('signup/', users.signup, name='signup'),
    path('update_password/<uuid:pk>', users.update_password, name='update_password'),

    path('authors/', authors.AuthorListLocal.as_view(), name='author_list_local'),
    path('authors/<uuid:author_id>', authors.AuthorDetailLocal.as_view(), name='author_detail'),
    path('authors/<uuid:author_id>/followers', follows.FollowerListLocal.as_view(), name='follower_list_local'),
    path('authors/<uuid:author_id>/profile_image', image.ProfileImage.as_view(), name='profile_image'),
    path('followers/', follows.FollowerListLocal.as_view(), name='follower_list_local'),
    path('followings/', follows.FollowingListLocal.as_view(), name='following_list_local'),
    
    path('friend-requests/', friend_request.FriendRequestList.as_view(), name='friend_request_list'),
    path('friend-requests/<uuid:friend_request_id>', friend_request.FriendRequestDetail.as_view(), name='friend_request_detail'),
    
    path('my-profile',authors.Profile.as_view(), name='my_profile'),
    
    path('posts/', posts.PostListLocal.as_view(), name='post_list_local'),
    path('posts/<uuid:post_id>', posts.PostDetailLocal.as_view(), name='post_detail_local'),
    path('posts/<uuid:post_id>/likes', likes.LikePostListLocal.as_view(), name='like_post_list_local'),
    path('posts/<uuid:post_id>/comments/', comments.CommentListLocal.as_view(), name='comment_list_local'),   
    path('posts/<uuid:post_id>/comments/<uuid:comment_id>/likes', likes.LikeCommentListLocal.as_view(), name='like_comment_list_local'),
    
    path('posts/<uuid:post_id>/image', image.PostImage.as_view(), name='post_image'),
    path('share-post/', posts.SharePost.as_view(), name='share_post'),
]