from api.models import Notification
from api.serializer import NotificationDetailSerializer, NotificationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status


class NotificationList(GenericAPIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]
  queryset = Notification.objects.all()
  serializer_class = NotificationDetailSerializer

  
  def get(self, request, **kwargs):
    user = Token.objects.get(key=request.auth).user
    notifications = Notification.objects.filter(user=user)
    serializer = NotificationDetailSerializer(notifications, many=True, context={'request': request})
    return Response(serializer.data)
  

class NotificationDetail(GenericAPIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]
  queryset = Notification.objects.all()
  serializer_class = NotificationSerializer
  lookup_url_kwarg = 'notification_id'
  
  def patch(self, request, **kwargs):
    notification = self.get_object()
    serializer = self.get_serializer(instance=notification, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)