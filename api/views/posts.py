import uuid
from ..models import User, Post, LikePost, Notification
from api.serializer import PostSerializer, LikePostSerializer, PostListItemSerializer, PostDetailSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework import status
from drf_spectacular.utils import extend_schema
from ..utils import get_visible_posts, update_access_permission
from .permissions import IsPostOwnerOrReadOnly, IsPostModifyPermissionOwner
from ..server_adapters.my_site_adapter import MySiteAdapter

# TO-DO: add auth tokens to all endpoints from login

class PostList(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    @extend_schema(
        responses={200: PostListItemSerializer(many=True)}
    )
    def get(self, request, **kwargs):
        user = Token.objects.get(key=request.auth).user
        posts = get_visible_posts(user)
        serializer = PostDetailSerializer(posts, many=True, context={'request': request})
        post_list = serializer.data
        
        adapter = MySiteAdapter()
        foriegn_authors = []
        foriegn_posts = []
        
        resp = adapter.request_get_author_list()
        if resp['status_code'] == 200:
            foriegn_authors = resp['body']
            
        for author in foriegn_authors:
            author_id = author['id'].split('/')[-1]
            resp = adapter.request_get_author_posts(author_id)
            if resp['status_code'] == 200:
                foriegn_posts.extend(resp['body'])
                
        return Response(post_list + foriegn_posts, status=status.HTTP_200_OK)
        
    
    @extend_schema(
        request=PostSerializer,
        responses={201: PostSerializer, 400: None}
    )
    def post(self, request, **kwargs):
        user = Token.objects.get(key=request.auth).user
        new_data = request.data
        new_data['author'] = user.id
        post_id = uuid.uuid4()
        new_data['id'] = post_id
        new_data['origin'] = f'{request.scheme}://{request.get_host()}/author/{user.id}/posts/{post_id}'
        new_data['source'] = new_data['origin']
        serializer = self.get_serializer(data=new_data)
        if serializer.is_valid():
            if new_data.get('visibility', 'public') == 'private' and not 'allowed_users' in new_data:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'allowed_users field is required for private posts'})
            
            allowed_user_ids = new_data.get('allowed_users', [])
            post = serializer.save()
            update_access_permission(post, allowed_user_ids)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

class PostDetail(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostOwnerOrReadOnly]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_url_kwarg = 'post_id'
     
    @extend_schema(
        responses={200: PostDetailSerializer, 404: None}
    )
    def get(self, request, **kwargs):
        post = self.get_object()
        self.check_object_permissions(request, post)
        serializer = PostDetailSerializer(post, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: None, 404: None}
    )
    def delete(self, request, **kwargs):
        post = self.get_object()
        self.check_object_permissions(request, post)
        post.delete()
        return Response({'message': 'Post deleted successfully'}, status=200)
    
    @extend_schema(
        request=PostSerializer,
        responses={200: PostSerializer, 400: None, 404: None}
    )
    def put(self, request, **kwargs):
        user = Token.objects.get(key=request.auth).user
        post = self.get_object()
        self.check_object_permissions(request, post)
        new_data = request.data
        new_data['author'] = user.id
        serializer = self.get_serializer(post, data=new_data, partial=True)
        allowed_user_ids = new_data.get('allowed_users', [])
        allowed_users = User.objects.filter(id__in=allowed_user_ids)
        update_access_permission(post, allowed_users)
    
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

class PostLikeList(GenericAPIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated, IsPostModifyPermissionOwner]
        queryset = LikePost.objects.all()
        serializer_class = LikePostSerializer
        lookup_url_kwarg = 'post_id'
        
        @extend_schema(
            responses={200: LikePostSerializer(many=True)}
        )
        def post(self, request, **kwargs):
            post = get_object_or_404(Post, id=kwargs['post_id'])
            self.check_object_permissions(request, post)
            user = Token.objects.get(key=request.auth).user
            like_body = request.data
            like_body['user'] = user.id
            like_body['post'] = post.id
            
            serializer = self.get_serializer(data=like_body)
            if serializer.is_valid():
                serializer.save()
                Notification.objects.create(user=post.author, author=user, post=post, type='LIKE_POST')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=400, data=serializer.errors)
        
        @extend_schema(
            responses={200: None, 400: None, 404: None}
        )   
        def delete(self, request, **kwargs):
            post = get_object_or_404(Post, id=kwargs['post_id'])
            self.check_object_permissions(request, post)
            user = Token.objects.get(key=request.auth).user
            query_result = LikePost.objects.filter(user=user.id, post=post.id)
            if not query_result.exists():
                return Response({'message': 'User has not liked post'}, status=status.HTTP_400_BAD_REQUEST)
            post.likes -= 1
            post.save()
            query_result.delete()
            return Response({'message': 'Like deleted successfully'}, status=200)

