from api.models import Follow, User
from api.serializer import  FollowerListSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class FollowerListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all().filter(is_server=False, is_superuser=False, is_foreign=False)
    serializer_class = FollowerListSerializer
    
    
    def get(self, request, **kwargs):
        author = request.user
        followers = Follow.objects.filter(target=author)
        data_set = set()
        for follower in followers:
            data_set.add(follower.follower)
        serializer = self.get_serializer(data_set, context = {'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
        