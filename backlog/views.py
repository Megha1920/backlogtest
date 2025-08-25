from rest_framework import viewsets
from .models import Project, TeamMember, Task, TaskStatusHistory
from .serializers import ProjectSerializer, TeamMemberSerializer, TaskSerializer, TaskStatusHistorySerializer,UserSerializer
from .permissions import IsAdmin, IsManager, IsTeamMember, IsManagerOrAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]  # allow all logged-in users

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Project.objects.all()
        elif user.role == 'manager':
            return Project.objects.filter(manager=user)
        elif user.role == 'member':
            return Project.objects.filter(team_members__member=user)
        return Project.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'admin':  # ✅ only admins can create
            raise PermissionDenied("Only admins can create projects.")
        serializer.save(created_by=self.request.user)



class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return TeamMember.objects.all()
        elif user.role == 'manager':
            # Managers can only see team members for their own projects
            return TeamMember.objects.filter(project__manager=user)
        elif user.role == 'member':
            # Members can only see themselves
            return TeamMember.objects.filter(member=user)
        return TeamMember.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data['project']

        if user.role == 'admin':
            serializer.save()
        elif user.role == 'manager':
            # Managers can only add members to projects they manage
            if project.manager != user:
                raise PermissionDenied("You cannot assign members to projects you don’t manage.")
            serializer.save()
        else:
            raise PermissionDenied("You don’t have permission to assign team members.")

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
        project = Project.objects.get(id=project_id)
        
        # Ensure only the project's manager can assign tasks
        if self.request.user.role != 'manager' or project.manager != self.request.user:
            raise PermissionDenied("You are not allowed to assign tasks for this project.")
        
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
    

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint for listing all users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]