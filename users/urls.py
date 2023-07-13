from .serializers import SignUpSerializer
from .views import CreateUserView,VerifyApiView,GetNewVarifyApiView,ChangeUserInfoView,ChangeUserPhotoView,LoginView,\
LoginRefreshView,LogoutView,ForgetPasswordView,ResetPasswordView
from django.urls import path


urlpatterns=[
    path('login/',LoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('signup/',CreateUserView.as_view()),
    path('verify/',VerifyApiView.as_view()),
    path('new-verify/',GetNewVarifyApiView.as_view()),
    path('change-user/',ChangeUserInfoView.as_view()),
    path('change-user-photo/',ChangeUserPhotoView.as_view()),
    path('login/refresh/',LoginRefreshView.as_view()),
    path('forgot-password/',ForgetPasswordView.as_view()),
    path('reset-password/',ResetPasswordView.as_view())

]