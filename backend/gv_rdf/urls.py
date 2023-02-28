from django.urls import path
from django.contrib import admin
from core import views as core_views
from projects import views as projects_views
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token


router = routers.DefaultRouter()

# Endpoint for creating new projects
# The user creating the project is the owner
# POST http://localhost:8000/project/
# {
#     "title": "",
#     "description": "",
#     "max_collaborators": ""
# }
router.register(r'project', projects_views.ProjectViewSet, basename='project')

# Endpoint for marking a project as Inactive (which is considered complete)
# PATCH http://localhost:8000/complete_project/<uuid pk of the project>/
# {
#     "status": 0
# }
router.register(r'complete_project', projects_views.CompleteProjectViewSet, basename='complete_project')

# Endpoint for getting the projects that have open seats
# GET   http://localhost:8000/open_project/
router.register(r'open_project', projects_views.OpenProjectViewSet, basename='open_project')

# Endpoint for expressing interest in a project as a user
# POST  http://localhost:8000/candidacy/
# {
#     "title": "project unique title"
# }
router.register(r'candidacy', projects_views.CandidacyViewSet, basename='candidacy')

#  maybe add a router ShowProjectCandidates which will return username, email and skills of interested users

# Endpoint for accepting or rejecting a candidate
# On accepting a candidate, the candidate is added as collaborator to the project
# PATCH http://localhost:8000/candidate_response/<uuid of the Candidate object>/
# 1: accept, 2: reject
# {
#     "reply_status": 1
# }
router.register(r'candidate_response', projects_views.CandidateResponseViewSet, basename='candidate_response')

urlpatterns = router.urls

urlpatterns += [
    path('admin/', admin.site.urls),

    # Endpoint for logging in as a user by returning an auth token
    # POST  http://localhost:8000/login/
    # {
    #     "username": "konn",
    #     "password": "1234!@#$"
    # }
    path('login/', obtain_auth_token),

    # Endpoint for registering as a new user
    # anyone can register, no authentication
    # POST  http://localhost:8000/register/
    # {
    #     "username": "",
    #     "password": "",
    #     "password2": "",
    #     "email": "",
    #     "first_name": "",
    #     "last_name": "",
    #     "address": "",
    #     "age": 23,
    #     "country": "GR"
    # }
    path('register/', core_views.RegisterView.as_view(), name='auth_register'),

    # Endpoint for changing user password
    # Password is changed for the authenticated user
    # POST  http://localhost:8000/change_password/
    # {
    #     "password": "",
    #     "password2": "",
    #     "old_password": "",
    # }
    path('change_password/<int:pk>/', core_views.ChangePasswordView.as_view(), name='auth_change_password'),

    # Endpoint for requesting password reset by providing a valid registered user email
    # It returns a reset token and a uidb64
    # It could be implemented by emailing a reset link
    # POST  http://localhost:8000/request-reset-email/
    # {
    #     "email": ""
    # }
    path('request-reset-email/', core_views.RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),

    # path('password-reset/<uidb64>/<token>/', core_views.PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),

    # Endpoint for resetting the user password by providing the reset token, the uidb64 and a new password
    # POST/PATCH    http://localhost:8000/password-reset-complete/
    # {
    #     "password": "",
    #     "token": "",
    #     "uidb64": "",
    # }
    path('password-reset-complete/', core_views.SetNewPasswordAPIView.as_view(), name='password-reset-complete'),

    # POST http://localhost:8000/update_profile/<uuid pk of the profile>/
    # {
    #     "email": "konn09@me.gg",
    #     "first_name": "konn",
    #     "last_name": "konn",
    #     "age": 45,
    #     "country": "GR",
    #     "address": "konn",
    #     "skills": [2, 8, 5]
    # }
    path('update_profile/<uuid:pk>/', core_views.UpdateProfileView.as_view(), name='auth_update_profile'),

    # POST http://localhost:8000/add_skill/
    # adds a skill to the logged-in (authenticated) user
    # {
    #     "skill": 2
    # }
    path('add_skill/', core_views.AddSkillView.as_view(), name='auth_add_skill'),

    # DELETE http://localhost:8000/remove_skill/<int pk of the skill>/
    path('remove_skill/<int:pk>/', core_views.RemoveSkillView.as_view(), name='auth_remove_skill'),
]
