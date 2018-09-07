from django.contrib.auth.models import User
from rest_framework import viewsets
from api.serializers import (WorkspaceCreateSerializer,
                             WorkspaceSerializer,
                             TaskSerializer,
                             MinidSerializer)
from api.permissions import IsOwner
from portal.models import Workflow, Task
from globus_portal_framework.search.models import Minid


class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows workspaces to be created/viewed/deleted.

    Workspaces are collections of tasks. Each task has an input minid, and
    an output minid. Computational tasks that create output minids will serve
    as inputs for the next task in the list. Tasks are ordered by id one after
    the other, the order cannot be changed after a task has been created.
    """
    queryset = Workflow.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = (IsOwner,)


    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'POST':
            serializer_class = WorkspaceCreateSerializer
        return serializer_class


    def get_queryset(self):
        return Workflow.objects.filter(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be created/viewed/deleted
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
