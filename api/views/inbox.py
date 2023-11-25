from api.models import User, Post, InboxItem, FriendRequest
from api.serializer import InboxSerializer
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..utils import get_or_create_foreign_user
import json


class InboxListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'author_id'
    queryset = InboxItem.objects.all()
    serializer_class = InboxSerializer
    
    
    def post(self, request, **kwargs):
        author = self.get_object()
        type = request.data.get('type', None)
        
        if type == "Follow":
          requester_data = request.data.get('actor', None)
          requester_obj = get_or_create_foreign_user(requester_data)
          if requester_obj:
            FriendRequest.objects.create(target=author, requester=requester_obj)
            InboxItem.objects.create(receiver=author, type=type, requester=requester_obj, item=json.dumps(request.data))
            return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
          
            
          