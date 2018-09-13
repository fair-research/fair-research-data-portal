from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from api.serializers import (WorkspaceCreateSerializer,
                             WorkspaceSerializer,
                             TaskSerializer,
                             MinidSerializer)
from api.permissions import IsOwner
from portal.models import Workspace, Task
from globus_portal_framework.search.models import Minid


class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows workspaces to be created/viewed/deleted.

    Workspaces are collections of tasks. Each task has an input minid, and
    an output minid. Computational tasks that create output minids will serve
    as inputs for the next task in the list. Tasks are ordered by id one after
    the other, the order cannot be changed after a task has been created.
    """
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = (IsOwner,)


    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'POST':
            serializer_class = WorkspaceCreateSerializer
        return serializer_class


    def get_queryset(self):
        return Workspace.objects.filter(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be created/viewed/deleted

    The additional following actions are supported for each task:
    * /start

    NOTICE! The `status` field is deprecated and will be removed. Please
    use `current_status` instead which guarantees the current state of a
    running task within a given time interval.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsOwner,)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('status',)

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    @action(methods=['get', 'post'], detail=True, url_path='start',
            url_name='start')
    def start(self, request, pk=None):
        task = self.get_object()
        if request.method == 'POST':
            task.start()
            # Update task info
            task = self.get_object()
        task_s = TaskSerializer(task, context={'request': request})
        return Response(task_s.data)
