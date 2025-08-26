from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import (
    ProjectViewSet,
    TeamMemberViewSet,
    TaskViewSet,
    ManagerListView,
    CurrentUserView,
    UserViewSet,
)

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename="project")
router.register('team-members', TeamMemberViewSet, basename="teammember")
router.register('tasks', TaskViewSet, basename="task")

router.register('users', UserViewSet, basename="user")

# NESTED ROUTER: /projects/:project_id/tasks/
project_tasks_router = NestedDefaultRouter(router, 'projects', lookup='project')
project_tasks_router.register('tasks', TaskViewSet, basename='project-tasks')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(project_tasks_router.urls)),  # include nested route
    path('managers/', ManagerListView.as_view(), name='manager-list'),
    path('user/', CurrentUserView.as_view(), name='current-user'),
]
