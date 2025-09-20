from rest_framework.generics import ListAPIView

from rest_framework.permissions import IsAuthenticated

from .models import Project
from .serializers import ProjectSerializer

class ProjectListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.prefetch_related('members').order_by('-updated_at')
    serializer_class = ProjectSerializer
