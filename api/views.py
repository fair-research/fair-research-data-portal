from rest_framework import viewsets
from api.serializers import WorkspaceSerializer
from api.permissions import IsOwner
from portal.models import Workflow


class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows workspaces to be created/viewed/deleted
    """
    queryset = Workflow.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return Workflow.objects.filter(user=self.request.user)
