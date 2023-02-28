from django.contrib.auth.models import User
from projects.models import Project, Candidate
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.test import APITestCase


class ProjectsTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='userTest',
            password='5678%^&*',
            email='userTest@test.com'
        )
        project = Project.objects.create(title="Test Project", description="bla bla bla", max_collaborators=7)
        Candidate.objects.create(user=self.user, project=project, reply_status=0)
        self.candidates = Candidate.objects.all()
        self.projects = Project.objects.all()

        # The app uses token authentication
        self.token = Token.objects.get(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_accept_candidate(self):
        for candidate in self.candidates:
            data = {"reply_status": 1}
            response1 = self.client.patch(f'/candidate_response/{0}/'.format(candidate.id), data)
            response2 = self.client.patch(f'/candidate_response/{0}/'.format(candidate.id), data)
            # the second accept should not execute, as it will create a duplicate Collaborator
            self.assertNotEqual(response1.status_code, response2.status_code)
