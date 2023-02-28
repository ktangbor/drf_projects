from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework.fields import IntegerField
from django_countries.fields import CountryField
from . import models
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]  # unique email across all users
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match!"})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'], email=validated_data['email'],
                                        password=validated_data['password'])
        user.save()

        profile = models.Profile.objects.create(
            user=user,
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        profile.save()

        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "New passwords do not match"})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Current password is not correct"})
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)


class UpdateProfileSerializer(serializers.ModelSerializer):
    # def __init__(self, *args, **kwargs):
    #     """If object is being updated don't allow username to change."""
    #     super().__init__(*args, **kwargs)
    #     if self.instance is not None:
    #         self.fields.get('username').read_only = True
    #         # self.fields.pop('parent') # or remove the field

    email = serializers.EmailField(required=True)
    age = IntegerField()
    country = CountryField()

    class Meta:
        model = models.Profile
        fields = ('email',
                  'first_name',
                  'last_name',
                  'address',
                  'age',
                  'country'
                  )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "New passwords do not match"})

        return attrs

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return value

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        instance.address = validated_data['address']
        instance.age = validated_data['age']
        instance.country = validated_data['country']
        instance.save()

        return instance


class AddSkillSerializer(serializers.ModelSerializer):
    skill = serializers.CharField()

    class Meta:
        model = models.ProgrammingSkill
        fields = ('skill',)

    def validate(self, attrs):
        user = self.context['request'].user
        profile = models.Profile.objects.get(user=user)
        skill_count = models.ProgrammingSkill.objects.filter(profile=profile).count()
        if models.ProgrammingSkill.objects.filter(profile=profile, skill=attrs['skill']).exists():
            raise serializers.ValidationError({"error": "Skill already exists"})
        if skill_count > 2:
            raise serializers.ValidationError({"error": "Maximum number of skills reached"})

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        profile = models.Profile.objects.get(user=user)
        skill = models.ProgrammingSkill.objects.create(skill=validated_data['skill'], profile=profile)
        skill.save()

        return skill
