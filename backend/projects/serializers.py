from . import models
from rest_framework_json_api import serializers
from .models import Collaborator, Project, Candidate


class ProjectSerializer(serializers.ModelSerializer):
    collaborators = serializers.PrimaryKeyRelatedField(queryset=Collaborator.objects.all(), many=True,
                                                       allow_null=True, default=None)

    class Meta:
        model = models.Project
        fields = ('title', 'description', 'max_collaborators', 'collaborators', 'status')
        extra_kwargs = {
            'title': {'required': True},
            'max_collaborators': {'required': True},
            'collaborators': {'required': False},
        }

    # def validate(self, attrs):
    #     user = self.context['request'].user
    #     profile = models.Profile.objects.get(user=user)
    #     g = models.ProgrammingSkill.objects.filter(profile=profile).count()
    #     if g > 2:
    #         raise serializers.ValidationError({"error": "g g g"})
    #
    #     return attrs


class OpenProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = ('title', 'description', 'max_collaborators', 'status')
        extra_kwargs = {
            'collaborators': {'required': False},
        }

    def validate(self, attrs):
        pass


class CandidacySerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = ('project', 'user', 'reply_status')
        extra_kwargs = {
            'project': {'required': True},
            'user': {'required': True}
        }

    def validate(self, attrs):
        return attrs


class CandidateResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = ('project', 'user', 'reply_status')
        extra_kwargs = {
            'project': {'required': False},
            'user': {'required': False}
        }

    def validate(self, attrs):
        return attrs
