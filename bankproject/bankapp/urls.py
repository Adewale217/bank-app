from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logoutAuth, name='logout'),
    path('signout/', views.signout, name='signout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("transfer/", views.transfer, name="transfer"),
    path("top-up/", views.top_up, name="top_up"),
]