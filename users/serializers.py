from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from .models import User, UserConfirmation, VIA_PHONE, VIA_EMAIL, NEW, CODE_VERIFIED, DONE, PHOTO_DONE
from django.db.models import Q
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from shared.utility import check_email_or_phone, send_email,check_user_type


class SignUpSerializer(serializers.ModelSerializer):

    id=serializers.UUIDField(read_only=True)

    def __init__(self,*args,**kwargs):
        super(SignUpSerializer,self).__init__(*args,**kwargs)
        self.fields['email_phone_number']=serializers.CharField(required=False)

    class Meta:
        model=User
        fields=(
            'id',
            'auth_type',
            'auth_status',
        )
        extra_kwargs={
            'auth_type':{'read_only':True,'required':False},
            'auth_status':{'read_only':True,'required':False}
        }

    def create(self, validated_data):
        user=super(SignUpSerializer,self).create(validated_data)
        print(user)
        if  user.auth_type==VIA_EMAIL:
            code=user.create_verify_code(VIA_EMAIL)
            print(code)
            send_email(user.email,code)

        elif user.auth_type==VIA_PHONE:
            code=user.create_verify_code(VIA_PHONE)
            print(code)
            # send_phone_code(user.phone_number,code)
            send_email(user.phone_number,code)
        user.save()
        return user

    def validate(self,data):
        super(SignUpSerializer,self).validate(data)
        data=self.auth_validate(data)
        return  data

    @staticmethod
    def auth_validate(data):

        user_input=str(data.get('email_phone_number'))
        input_type=check_email_or_phone(user_input)

        if input_type=='email':
            data={
                'auth_type':VIA_EMAIL,
                'email':user_input
            }

        elif input_type=='phone':
            data={
                'auth_type':VIA_PHONE,
                'phone_number':user_input
            }
        else:
            data={
                'success':False,
                'message':'you must send email or phone number'
            }

            raise ValidationError(data)


        print('user_input',user_input)
        print('input_type',input_type)
        print(data)

        return data

    def to_representation(self, instance):
        print('to_rep',instance)
        data=super(SignUpSerializer,self).to_representation(instance)
        data.update(instance.token())
        return data
    def validate_email_phone_number(self,value):
        value=value.lower()
        if value and User.objects.filter(email=value).exists():
            data={
                'success':False,
                'message':'bu email allqachon royxatdam otgan',
            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data={
                'success':False,
                'message':"bu raqam allaqacho ro'yxatdam o'tgan"
            }

            raise ValidationError(data)
        return value
class ChangeUserInfo(serializers.Serializer):
    first_name=serializers.CharField(write_only=True,required=True)
    last_name=serializers.CharField(write_only=True,required=True)
    username=serializers.CharField(write_only=True,required=True)
    password=serializers.CharField(write_only=True,required=True)
    confirm_password=serializers.CharField(write_only=True,required=True)

    def validate(self,data):
        password=data.get('password',None)
        confirm_password=data.get('confirm_password',None)

        if password !=confirm_password:
            raise ValidationError({
                'message':'confirmation password doesnt match'
            })
        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data

    def validate_username(self,username):
        if len(username)<5 or len(username)>35:
            raise ValidationError(
                {
                    'message':'username must be berween 5 and 35 characters long'
                }
            )
        if username.isdigit():
            raise ValidationError(
                {
                    'message':'your username is entirely numeric '
                }
            )
        return username
    def validate_first_name(self,first_name):
        if len(first_name)<5 or len(first_name)>35:
            raise ValidationError(
                {
                    'message':'firs_name must be berween 5 and 35 characters long'
                }
            )
        if first_name.isdigit():
            raise ValidationError(
                {
                    'message':'your first_name is entirely numeric '
                }
            )
        return first_name
    def validate_last_name(self,last_name):
        if len(last_name)<5 or len(last_name)>35:
            raise ValidationError(
                {
                    'message':'last_name must be berween 5 and 35 characters long'
                }
            )
        if last_name.isdigit():
            raise ValidationError(
                {
                    'message':'your last_name is entirely numeric '
                }
            )
        return last_name

    def update(self, instance, validated_data):
        instance.username=validated_data.get('username',instance.username)
        instance.last_name=validated_data.get('last_name',instance.last_name)
        instance.first_name=validated_data.get('first_name',instance.first_name)
        instance.password=validated_data.get('password',instance.password)

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status==CODE_VERIFIED:
            instance.auth_status=DONE

        instance.save()
        return instance


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo=serializers.ImageField(validators=[FileExtensionValidator(
        allowed_extensions=['jpg','jpeg','heic','heif','png']
    )])
    def update(self, instance, validated_data):
        photo=validated_data.get('photo')
        if photo:
            instance.photo=photo
            instance.auth_status=PHOTO_DONE
            instance.save()
        return instance

class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self,*args,**kwargs):
        super(LoginSerializer,self).__init__(*args,**kwargs)
        self.fields['userinput']=serializers.CharField(required=True)
        self.fields['username']=serializers.CharField(required=False, read_only=True)

    def auth_validate(self,data):
        user_input=data.get('userinput')

        if check_user_type(user_input)=='username':
             user=self.get_user(username__iexact=user_input)
             username=user.username

        elif check_user_type(user_input)=='email':
            user=self.get_user(email__iexact=user_input)
            username=user.username
        elif check_user_type(user_input)=='phone':
            user=self.get_user(phone_number=user_input)
            username=user.username

        else:
            raise ValidationError(
                {
                    'success':False,
                    'message':'siz email username yoki raqam jonatishiz kerak'
                }
            )
        authentication_kwargs= {
                self.username_field:username,
                'password': data['password']
        }
        current_user=User.objects.filter(username=username).first()
        if current_user.auth_status in [NEW,CODE_VERIFIED]:
            raise ValidationError(
                {
                    'success':False,
                    'message':'siz royxatdan toliq otmagansiz'
                }
            )
        user=authenticate(**authentication_kwargs)
        if user is not None:
            self.user=user

        else:
            raise ValidationError(
                {
                    'success':False,
                    'message':'username or password you enterred is incorrect , check and try again !'
                }
            )


    def validate(self,data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE,PHOTO_DONE]:
            raise PermissionDenied('siz hali toliq registratsiyadan otmaganingiz sababli login qila olmaysiz !')
        data=self.user.token()
        data['auth_status']=self.user.auth_status
        data['full_name']=self.user.full_name
        return data
    def get_user(self,**kwargs):
        users=User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError(
                {
                    'message':"no active user found"
                }
            )
        return users.first()

class LoginRefresgSerializer(TokenRefreshSerializer):

    def validate(self,attrs):
        data=super().validate(attrs)
        access_token_instance=AccessToken(data['access'])
        user_id=access_token_instance['user_id']
        user=get_object_or_404(User,id=user_id)
        update_last_login(None,user)
        return data

class LogoutSerializer(serializers.Serializer):
    refresh=serializers.CharField

class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone=serializers.CharField(write_only=True,required=True)
    def validate(self,attrs):
        email_or_phone=attrs.get('email_or_phone',None)
        if email_or_phone is None:
            raise ValidationError(
                {
                    'success':False,
                    "message":'you have to input email or your phone number'
                }
            )
        user=User.objects.filter(Q(phone_number=email_or_phone) | Q(email=email_or_phone))
        if not user.exists():
            raise NotFound(detail="no users found")
        attrs['user']=user.first()

        return attrs

class ResetPasswordSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    password=serializers.CharField(required=True,write_only=True)
    confirm_password=serializers.CharField(required=True,write_only=True)

    class Meta:
        model=User
        fields=(
            'id','password','confirm_password'
        )

    def validate(self,data):
        password=data.get('password',None)
        confirm_password=data.get('confirm_password',None)
        if password !=confirm_password:
            raise ValidationError(
                {
                    'success':False,
                    'message':'passwordlaringiz bir biriga mos emas, iltimos tekshirib qaytadan urinib koring'
                }
            )
        if password:
            validate_password(password)

        return data
    def update(self, instance, validated_data):
        password=validated_data.pop('password')
        instance.set_password(password)
        return super(ResetPasswordSerializer,self).update(instance,validated_data)