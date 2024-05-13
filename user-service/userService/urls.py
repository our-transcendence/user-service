"""
URL configuration for userService project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from user import endpoints

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', endpoints.create_user),
    path('<int:user_id>/infos', endpoints.get_user),
    path('<int:user_id>/update', endpoints.update_user),
    path('<int:user_id>/picture', endpoints.get_picture),
    path('<int:user_id>/delete', endpoints.delete_user),
<<<<<<< HEAD
    path('friends', endpoints.get_friends),
    path('friends_rec', endpoints.get_friend_rec),
    path('friend_send', endpoints.get_friend_send),
    path('add_friend/<int:friend_id>', endpoints.add_friend),
=======
	path('test/', endpoints.test)
>>>>>>> main
]
