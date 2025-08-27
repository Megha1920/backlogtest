from rest_framework import viewsets
from .models import Project, TeamMember, Task, TaskStatusHistory
from .serializers import ProjectSerializer, TeamMemberSerializer, TaskSerializer, TaskStatusHistorySerializer,UserSerializer
from .permissions import IsAdmin, IsManager, IsTeamMember, IsManagerOrAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.db.models import Q
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]  # allow all logged-in users

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            # Admin sees projects they created OR are a team member of
            return Project.objects.filter(
                Q(created_by=user) | Q(team_members__member=user)
            ).distinct()
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
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        project_id = self.kwargs.get("project_pk")

        queryset = Task.objects.all()

        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Restrict members only for the LIST view, not for retrieving a single task
        if hasattr(user, "role") and user.role == "member" and self.action == "list":
            queryset = queryset.filter(assigned_to=user)

        return queryset


        return queryset

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_pk")
        project = Project.objects.get(id=project_id)

        # Ensure only the project's manager can assign tasks
        if self.request.user.role != "manager" or project.manager != self.request.user:
            raise PermissionDenied("You are not allowed to assign tasks for this project.")

        serializer.save(created_by=self.request.user, project=project)

    # 🔑 Allow members to update only the status of their tasks
    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user

        if user.role == "member":
            # Members can only update tasks assigned to them
            if task.assigned_to != user:
                raise PermissionDenied("You cannot update tasks not assigned to you.")

            # Members can only change status
            if "status" not in request.data or len(request.data.keys()) > 1:
                raise PermissionDenied("You can only update the status of your tasks.")

        return super().partial_update(request, *args, **kwargs)

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