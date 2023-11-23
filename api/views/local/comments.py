from api.models import Comment, Post, LikeComment, Notification
from api.serializer import CommentSerializer, LikeCommentSerializer,CommentDetailSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework import status
from drf_spectacular.utils import extend_schema
from api.permissions import IsPostModifyPermissionOwner, IsCommentOwnerOrReadOnly, IsCommentModifyPermissionOwner


# TO-DO: add auth tokens to all endpoints from login
class CommentList(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostModifyPermissionOwner]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    @extend_schema(
        responses={200: CommentDetailSerializer(many=True), 404: None}
    )
    def get(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs['post_id'])
        self.check_object_permissions(request, post)
        comments = Comment.objects.filter(post=post.id)
        serializer = CommentDetailSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        request=CommentSerializer,
        responses={201: CommentDetailSerializer, 400: None, 404: None}
    )
    def post(self, request, **kwargs):
        user = Token.objects.get(key=request.auth).user
        post = get_object_or_404(Post, id=kwargs['post_id'])
        self.check_object_permissions(request, post)
        new_data = request.data
        new_data['user'] = user.id
        new_data['post'] = post.id
        serializer = self.get_serializer(data=new_data)
        if serializer.is_valid():
            serializer.save()
            comment_detail_serializer = CommentDetailSerializer(serializer.instance, context={'request': request})
            if post.author != user:
                Notification.objects.create(author=user, user=post.author, post=post, comment=serializer.instance, type='COMMENT_POST')
            return Response(comment_detail_serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

class CommentDetail(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCommentOwnerOrReadOnly]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_url_kwarg = 'comment_id'
    
    @extend_schema(
        responses={200: CommentDetailSerializer, 404: None}
    )
    def get(self, request, **kwargs):
        comment = self.get_object()
        self.check_object_permissions(request, comment)
        serializer = CommentDetailSerializer(comment, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        request=CommentSerializer,
        responses={200: CommentDetailSerializer, 400: None, 404: None}
    )
    def put(self, request, **kwargs):
        user = Token.objects.get(key=request.auth).user
        comment = self.get_object()
        self.check_object_permissions(request, comment)
        new_data = request.data
        new_data['user'] = user.id
        serializer = self.get_serializer(comment, data=new_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
    
    @extend_schema(
        responses={200: None, 404: None}
    )
    def delete(self, request, **kwargs):
        comment = self.get_object()
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response({'message': 'Comment deleted successfully'}, status=200)
    
class LikeCommentList(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCommentModifyPermissionOwner]
    queryset = LikeComment.objects.all()
    serializer_class = LikeCommentSerializer
    
    @extend_schema(
        request=None,
        responses={200: LikeCommentSerializer(many=True), 404: None}
    )
    def post(self, request, **kwargs):
        user = Token.objects.get(key=request.auth).user
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        self.check_object_permissions(request, comment)
        new_data = request.data
        new_data['user'] = user.id
        new_data['comment'] = comment.id
        serializer = self.get_serializer(data=new_data)
        if serializer.is_valid():
            serializer.save()
            if comment.user != user:
                Notification.objects.create(author=user, user=comment.user, comment=comment, post=comment.post, type='LIKE_COMMENT')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @extend_schema(
        responses={200: None, 404: None}
    )
    def delete(self, request, **kwargs):
        user = Token.objects.get(key=request.auth).user
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        self.check_object_permissions(request, comment)
        like = get_object_or_404(LikeComment, user=user.id, comment=comment.id)
        like.delete()
        return Response({'message': 'Like deleted successfully'}, status=200)