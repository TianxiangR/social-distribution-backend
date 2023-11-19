from django.contrib.auth import authenticate
from ..models import User, LikePost
from rest_framework.decorators import api_view
from django.http import JsonResponse
from ..serializers.insite_serializers import LikePostSerializer, UserSerializer, UserInfoSerializer
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

# TO-DO: add auth tokens to all endpoints from login
@extend_schema(
    request=UserSerializer,
    responses={200: None,  400: None, 404: None}
)
@api_view(['POST'])
def signup(request):
    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Signup successful'}, status=200)
        else:
            return JsonResponse(serializer.errors, status=400)
        
@extend_schema(
    responses={200: UserSerializer(many=True), 404: None}
)

class UserList(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get(self, request, **kwargs):
        users = User.objects.all()
        serializer = UserInfoSerializer(users, many=True, context={'request': request})
        
        returned_users = []
        # remove current user from list
        for user in serializer.data:
            # turn uuid into string for comparison
            if str(user['id']) != str(request.user.id):
                returned_users.append(user)
                
        return Response(returned_users, status=status.HTTP_200_OK)
    
class UserDetail(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_url_kwarg = 'user_id'
    
    def get(self, request, **kwargs):
        user = self.get_object()
        serializer = UserInfoSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'User updated successfully'}, status=200)
        else:
            return JsonResponse(serializer.errors, status=400)
        
    def delete(self, request, **kwargs):
        user = self.get_object()
        user.delete()
        return JsonResponse({'message': 'User deleted successfully'}, status=200)
        
@api_view(['POST'])
def update_password(request, pk):
    if request.method == "POST":
        try:
            user = User.objects.get(id=pk)
            user.set_password(request.data.get('password'))
            user.save()
            return JsonResponse({'message': 'Password updated successfully'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=404)

@extend_schema(
    request=dict,
    responses={200: UserSerializer(many=True), 404: None}
)
@api_view(['POST'])
def signin(request):
    if request.method == "POST":
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key, 'message': 'Login successful', 'user_id': user.id}, status=200)
        else:
            return JsonResponse({'message': 'Login unsuccessful'}, status=400)

@api_view(['GET'])
def get_likes_for_user(request, pk):
    if request.method == "GET":
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=200)
        likes = LikePost.objects.filter(user=user)
        serializer = LikePostSerializer(likes, many=True)
        return JsonResponse(serializer.data, safe=False)