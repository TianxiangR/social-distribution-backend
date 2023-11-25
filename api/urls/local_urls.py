from django.urls import path

from ..views import users

urlpatterns = [
    # insite apis
    path('login/', users.signin, name='login'),
    path('signup/', users.signup, name='signup'),
    path('update_password/<uuid:pk>', users.update_password, name='update_password'),

    path('authors', users.UserList.as_view(), name='authors'),
    
]