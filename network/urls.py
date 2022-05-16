
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newpost", views.newpost, name="newpost"),
    path("following", views.following, name="following"),
    path("profile", views.profile, name="profile"),
    path("likeapi/<post_id>", views.likeapi, name="likeapi")
]
