from json import JSONDecodeError
from django.http import JsonResponse
from .serializers import ProjectSerializer, OpenProjectSerializer, CandidacySerializer, CandidateResponseSerializer
from .models import Project, Collaborator, Candidate
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, RetrieveModelMixin
from django.db.models import Count
from itertools import chain


class ProjectViewSet(
        ListModelMixin,
        RetrieveModelMixin,
        UpdateModelMixin,
        viewsets.GenericViewSet
        ):

    """
    Endpoint for creating new projects
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer
    parser_classes = [JSONParser]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(user=user)

    def create(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = ProjectSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                user = request.user
                project = Project.objects.create(
                    title=data['title'], description=data['description'],
                    max_collaborators=data['max_collaborators'], user=user)
                project.save()
                return Response(ProjectSerializer(project).data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error", "message": "Json decoding error"}, status=400)


class CompleteProjectViewSet(
        ListModelMixin,
        UpdateModelMixin,
        viewsets.GenericViewSet
        ):

    """
    Endpoint for marking a project as Inactive (which is considered complete)
    """

    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser]
    serializer_class = ProjectSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(user=user)


class OpenProjectViewSet(
        ListModelMixin,
        RetrieveModelMixin,
        viewsets.GenericViewSet
        ):

    """
    Endpoint for getting the projects that have open seats
    Currently it is not filtering the Inactive (completed) projects (it should though)
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = OpenProjectSerializer
    parser_classes = [JSONParser]

    def get_queryset(self):
        result = (Collaborator.objects
                  .values('project')
                  .annotate(dcount=Count('project'))
                  .order_by()
                  )
        if result:
            # get projects with collaborators and open seats
            l1 = Project.objects.filter(max_collaborators__gt=result.dcount)

            # get projects with no collaborators and open seats
            l2 = Project.objects.filter(max_collaborators__gt=0).exclude(max_collaborators__gt=result.dcount)

            return list(chain(l1, l2))
        else:
            return Project.objects.filter(max_collaborators__gt=0)


class CandidacyViewSet(
        ListModelMixin,
        UpdateModelMixin,
        viewsets.GenericViewSet
        ):

    """
    Endpoint for expressing interest in a project as a user
    The user may be the creator of the project (but an auto-accept feature is not implemented for that case)
    """

    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser]
    serializer_class = CandidacySerializer

    def create(self, request):
        try:
            data = JSONParser().parse(request)
            user = self.request.user
            project = Project.objects.get(title=data['title'])
            cand = Candidate.objects.create(
                user=user,
                project=project,
                reply_status=0
            )
            cand.save()
            return Response(CandidacySerializer(cand).data)
        except JSONDecodeError:
            return JsonResponse({"result": "error", "message": "Json decoding error"}, status= 400)

    def get_queryset(self):
        """ not gonna use GET with this ViewSet"""
        pass
        # user = self.request.user
        # return Candidate.objects.filter(user=user)


class CandidateResponseViewSet(
        ListModelMixin,
        UpdateModelMixin,
        viewsets.GenericViewSet
        ):

    """
    Endpoint for accepting or rejecting a candidate
    """

    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser]
    serializer_class = CandidateResponseSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CandidateResponseSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if request.data['reply_status'] == 1:
                cand = Candidate.objects.get(pk=self.kwargs['pk'])
                collab = Collaborator.objects.create(
                    user=cand.user,
                    project=cand.project
                )
                collab.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data="wrong parameters", status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_queryset(self):
        #  not a good filter, but this ViewSet is to be used for PATCH only
        return Candidate.objects.filter()
