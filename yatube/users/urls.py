from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from . import views

app_name = 'users'
template_name1 = 'users/password_reset_form.html'
template_name2 = 'users/password_reset_done.html'
template_name3 = 'users/password_change_form.html'
template_name4 = 'users/password_change_done.html'
template_name5 = 'users/password_reset_confirm.html'
template_name6 = 'users/password_reset_complete.html'

urlpatterns = [
    path('logout/',
         LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),
    path('signup/',
         views.SignUp.as_view(template_name='users/signup.html'),
         name='signup'),
    path('login/',
         LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('password_reset/',
         PasswordResetView.as_view(template_name=template_name1),
         name='password_reset_form'),
    path('password_reset/done/',
         PasswordResetDoneView.as_view(template_name=template_name2),
         name='password_reset_done'),
    path('password_change/',
         PasswordChangeView.as_view(template_name=template_name3),
         name='password_change_form'),
    path('password_change/done/',
         PasswordChangeDoneView.as_view(template_name=template_name4),
         name='password_change_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name=template_name5),
         name='password_reset_confirm'),
    path('reset/done/',
         PasswordResetCompleteView.as_view(template_name=template_name6),
         name='password_reset_complete'),
]
