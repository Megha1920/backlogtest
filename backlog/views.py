from rest_framework import viewsets
from .models import Project, TeamMember, Task, TaskStatusHistory
from .serializers import ProjectSerializer, TeamMemberSerializer, TaskSerializer, TaskStatusHistorySerializer,UserSerializer
from .permissions import IsAdmin, IsManager, IsTeamMember, IsManagerOrAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()  # required for router registration
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Project.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)



class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated, IsManager]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()  # ← ADD THIS LINE
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return Task.objects.filter(project_id=project_id)
        return Task.objects.all()

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = Project.objects.get(id=project_id) if project_id else None
        serializer.save(created_by=self.request.user, project=project)



class TaskStatusHistoryViewSet(viewsets.ModelViewSet):
    queryset = TaskStatusHistory.objects.all()
    serializer_class = TaskStatusHistorySerializer
    permission_classes = [IsAuthenticated]


from dj_rest_auth.registration.views import RegisterView
from backlog.serializers import CustomRegisterSerializer

class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


from django.contrib.auth import get_user_model
User = get_user_model()  # ✅ Add this line

class ManagerListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        managers = User.objects.filter(role='manager')  # now User is defined
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)