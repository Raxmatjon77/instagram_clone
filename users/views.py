from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from rest_framework import permissions
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_email, check_email_or_phone
from .serializers import SignUpSerializer, ChangeUserInfo, ChangeUserPhotoSerializer, LoginSerializer, \
    LoginRefresgSerializer, LogoutSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User, UserConfirmation, NEW, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE


# Create your views here.
# class CreareUser(CreateAPIView):
#     serializer_class = SignUpSerializer
#     permission_classes =(permissions.AllowAny)
#     queryset=User.objects.all()

class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer


class VerifyApiView(APIView):
    permission_classes = (IsAuthenticated ,)


    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)
        return Response(
            data={
                "success": True,
                "auth_status": user.auth_status,
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token']
            }
        )



    @staticmethod
    def check_verify(user,code):
        verifies=user.verify_codes.filter(expiration_time__gte=datetime.now(),code=code,is_confirmed=False)

        if not verifies.exists():
            data={
                'message':'tasdiqlash kodingiz xato yoki eskirgan !'

            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)

        if user.auth_status==NEW:

            user.auth_status=CODE_VERIFIED
            user.save()
        return True
class GetNewVarifyApiView(APIView):
    permission_classes=[IsAuthenticated,]

    def get(self,request,*args,**kwargs):
          user=self.request.user
          self.check_varification(user)
          if user.auth_type==VIA_EMAIL:
            code= user.create_verify_code(VIA_EMAIL)
            send_email(user.email,code)
          elif user.auth_type==VIA_PHONE:
              code=user.create_verify_code(VIA_PHONE)
              send_email(user.phone_number,code)

          else:
             data={
              'message':'email yoki raqam notogri'
           }
             raise ValidationError(data)

          return Response(
              {
                  'success':True,
                  'message':'code qaytadan yuborildi !'
              }
          )

    @staticmethod
    def check_varification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                "message": "Kodingiz hali ishlatish uchun yaroqli. Biroz kutib turing"
            }
            raise ValidationError(data)
class ChangeUserInfoView(UpdateAPIView):
    serializer_class = ChangeUserInfo
    permission_classes = [IsAuthenticated,]
    http_method_names = ['patch','put']

    def get_object(self):
        return self.request.user
    def update(self, request, *args, **kwargs):
        super(ChangeUserInfoView,self).update(request,*args,**kwargs)
        data={
            'success':True,
            'message':'successfuly updated',
            'auth_status':self.request.user.auth_status

        }
        return Response(data,status=200)
    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInfoView,self).partial_update(request,*args,**kwargs)
        data={
            'success':True,
            'message':'successfuly updated',
            'auth_status':self.request.user.auth_status

        }
        return Response(data)


class ChangeUserPhotoView(APIView):
    permission_classes=[IsAuthenticated,]

    def put(self,request,*args,**kwargs):
        serializer=ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user=request.user
            serializer.update(user,serializer.validated_data)

            return Response(
                {
                    'message':'rasm muvaffaqiyatli yuklandi !'
                },status=200
            )

        return Response(serializer.errors,status=400)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefresgSerializer

class LogoutView(APIView):
    serializer_class=LogoutSerializer
    permission_classes=[IsAuthenticated,]

    def post(self,request,*args,**kwargs):
        serializer=self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token=self.request.data['refresh']
            token=RefreshToken(refresh_token)
            token.blacklist()
            data={
                'success':True,
                'message':"you are successfuly logged out"

            }
            return Response(data,status=205)

        except TokenError:
            return Response(status=400)
class ForgetPasswordView(APIView):
    permission_classes=[AllowAny,]
    serializer_class=ForgotPasswordSerializer
    def post(self,request,*args,**kwargs):
        serializer=self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data.get('user')
        email_or_phone=serializer.validated_data.get('email_or_phone')
        if check_email_or_phone(email_or_phone)=='email':
            code=user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone,code)
        elif check_email_or_phone(email_or_phone) == 'phone':
            code = user.create_verify_code(VIA_PHONE)
            send_email(email_or_phone, code)

        return Response(
            {
                'success':True,
                "message":"tasdiqlash kodi muvaffaqiyatli yuborildi",
                'access':user.token()['access'],
                'refresh':user.token()['refresh_token'],
                'auth_status':user.auth_status
            },status=200
        )
class ResetPasswordView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes=[IsAuthenticated,]
    http_method_names = ['patch','put']

    def get_object(self):
        return self.request.user
    def update(self, request, *args, **kwargs):
        response=super(ResetPasswordView,self).update(request,*args,**kwargs)

        try:
            user=User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(detail='no user found')
        return Response(
            {
                'success':True,
                'message':"parolingiz muvaffaqiyatli o'zgartirilidi",
                'access':user.token()['access'],
                'refresh':user.token()['refresh_token']
            }
        )
