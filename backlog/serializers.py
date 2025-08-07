from rest_framework import serializers
from .models import User, Project, TeamMember, Task, TaskStatusHistory

from dj_rest_auth.registration.serializers import RegisterSerializer

class CustomRegisterSerializer(RegisterSerializer):
    _has_phone_field = False
    def __init__(self, *args, **kwargs):
        print("🔥 CustomRegisterSerializer is ACTIVE")
        super().__init__(*args, **kwargs)

    # @property
    # def _has_phone_field(self):
    #     return False


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')

class ProjectSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='manager')
    )
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class TeamMemberSerializer(serializers.ModelSerializer):
    member = UserSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'

class TaskStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = TaskStatusHistory
        fields = '__all__'


from dj_rest_auth.serializers import LoginSerializer
class CustomLoginSerializer(LoginSerializer):
    username = None  # disable username login
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid login credentials")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        attrs['user'] = user
        return attrs