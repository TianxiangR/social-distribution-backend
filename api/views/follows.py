from ..models import User, Follow
from ..serializers.insite_serializers import FollowSerializer, UserInfoSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView,get_object_or_404
from rest_framework import status
import uuid
from drf_spectacular.utils import extend_schema


class FollowList(GenericAPIView):
  permission_classes = [IsAuthenticated]
  authentication_classes = [TokenAuthentication]
  serializer_class = FollowSerializer
  
  @extend_schema(
    request=FollowSerializer,
    responses={201: FollowSerializer, 400: None, 404: None}
  )
  def put(self, request, **kwargs):
    user = Token.objects.get(key=request.auth).user
    new_data = request.data
    new_data['follower'] = user.id
    following = get_object_or_404(User, id=request.data.get('target', '')) # check if the target user exists
    if following.id == user.id:
      return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'You cannot follow yourself'})
    new_data['following'] = following.id
    serializer = self.get_serializer(data=new_data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
  
  @extend_schema(
    responses={200: FollowSerializer(many=True), 404: None}
  )
  def delete(self, request, **kwargs):
    user = Token.objects.get(key=request.auth).user
    following = get_object_or_404(User, id=request.data.get('target', ''))
    print("follower found" , user.id)
    print("following found" , following.id)
    follow = get_object_or_404(Follow, follower=user.id, following=following.id)
    follow.delete()
    return Response({'message': 'Unfollowed successfully'}, status=status.HTTP_200_OK)

  @extend_schema(
    responses={200: UserInfoSerializer(many=True), 404: None}
  )
  def get(self, request, **kwargs):
    user = Token.objects.get(key=request.auth).user
    user_followers_query = user.follower_relations.all()
    user_following_query = user.following_relations.all()
    
    user_followers_id = [user_follower.follower.id for user_follower in user_followers_query]
    user_following_id = [user_following.following.id for user_following in user_following_query]
    
    # object filter using list of keywords: https://stackoverflow.com/questions/5956391/django-objects-filter-with-list
    user_followers = User.objects.filter(id__in=user_followers_id)
    user_followings = User.objects.filter(id__in=user_following_id)
    
    user_followers_serializer = UserInfoSerializer(user_followers, many=True, context={'request': request})
    user_followings_serializer = UserInfoSerializer(user_followings, many=True, context={'request': request})
    
    type_query = request.query_params.get('type', '')
    
    if type_query != '' and type_query not in ['friends', 'followers', 'following']:
      return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Invalid query parameter'})
    
    if type_query == 'friends':
      friends = [user_follower for user_follower in user_followers if user_follower in user_followings]
      friends_serializer = UserInfoSerializer(friends, many=True, context={'request': request})
      return Response(friends_serializer.data, status=status.HTTP_200_OK)
    
    if type_query == 'followers':
      response_body = user_followers_serializer.data
      for user_follower in response_body:
        user_follower['is_following'] = uuid.UUID(user_follower['id']) in user_following_id
      
      return Response(user_followers_serializer.data, status=status.HTTP_200_OK)
    
    if type_query == 'following':
      return Response(user_followings_serializer.data, status=status.HTTP_200_OK)
    
    response_body = {
      'followers': user_followers_serializer.data,
      'following': user_followings_serializer.data
    }
    return Response(response_body, status=status.HTTP_200_OK)
  