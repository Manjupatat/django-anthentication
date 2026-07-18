# from django.urls import path
# from . import views
# from .views import *
# # from demo_project.urls import urlpatterns
#
# urlpatterns = [
#     # path("", views.home, name='home')
#
# path('login/', views.login_view, name='login'),
# path('signup/', views.sign_up, name='signup'),
# path('', views.home_view, name='home'),
# ]
from tkinter.font import names

from django.urls import path
from . import views

urlpatterns = [

    path("", views.home_view, name="home"),

    path("login/", views.login_view, name="login"),

    path("forgot_password/", views.forgot_password_view, name="forgot_password"),
    path("verify-reset-otp/", views.verify_reset_otp_view, name="verify_reset_otp"),
    path("reset-password/", views.reset_password_view, name="reset_password"),

    path("signup/", views.signup_view, name="signup"),

    path("verify-otp/", views.verify_otp_view, name="verify_otp"),

    path("complete-signup/", views.complete_signup_view, name="complete_signup"),

    path("logout/", views.logout_view, name="logout"),

]