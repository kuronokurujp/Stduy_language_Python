from django.urls import path
from django.contrib.auth.views import LogoutView
from Accounts.views import MyLoginView, SignupView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
