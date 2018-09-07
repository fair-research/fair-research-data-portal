import logging
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from globus_portal_framework.search.models import Minid
from portal.models import Workflow, Task
from portal.workflow import (TASK_TASK_NAMES, TASK_WES, TASK_METADATA,
                             TASK_READY, TASK_WAITING)
from portal.minid import add_minid

log = logging.getLogger(__name__)


class MinidSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Minid
        fields = ('id', 'landing_page')

class TaskSerializer(serializers.HyperlinkedModelSerializer):

    input = MinidSerializer(many=True, read_only=True)
    output = MinidSerializer(many=True, read_only=True)
    category = serializers.CharField(read_only=True)
    data = serializers.JSONField(read_only=True)
    workflow = serializers.HyperlinkedRelatedField(read_only=True,
                                                   view_name='workflow-detail')

    class Meta:
        model = Task
        fields = ('id', 'url', 'category', 'workflow', 'data', 'input',
                  'output')


class WorkspaceCreateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Workflow
        fields = ('metadata', 'input_minid', 'tasks')

    task_type_h = ('Tasks to add to this workspace, as a JSON List. Example: '
                   '["WES", "JUPYTERHUB"]. Valid tasks are: {}'
                   ''.format(','.join(TASK_TASK_NAMES.keys())))
    input_minid_h = ('The minid that will serve as input for the first task '
                     'in the list.')
    metadata_h = ('A dictionary object about the workspace. Suggested you '
                  'include: assignment, seq, nwdid')

    tasks = serializers.JSONField(write_only=True,
                                           help_text=task_type_h)
    input_minid = serializers.CharField(write_only=True,
                                        help_text=input_minid_h)
    metadata = serializers.JSONField(write_only=True, help_text=metadata_h)

    def validate_metadata(self, metadata):
        if metadata is None or not isinstance(metadata, dict):
            raise ValidationError("Wrong type, must be of type '{}'")
        defaults = {
            'assignment': 'ungrouped',
            'seq': 'unspecified',
            'nwdid': ''
        }
        defaults.update(metadata)
        return defaults

    def validate_workspace_tasks(self, tasks):
        if not tasks:
            tasks = [TASK_WES]
        if not isinstance(tasks, list):
            raise ValidationError('Wrong type, please add as a string')
        return tasks

    def validate_input_minid(self, minid):
        valid_minids = ['ark:/99999/', 'ark:/57799/']
        if not any([minid.startswith(v) for v in valid_minids]):
            raise ValidationError('Must be a valid test or production Minid')
        return minid

    def create(self, validated_data):
        user = self.context['request'].user
        metadata = validated_data['metadata']
        tasks = validated_data['tasks']
        wname = '{} Topmed {}'.format(metadata['assignment'], metadata['seq'])
        workflow = Workflow(name=wname, user=user,
                            metadata=metadata)
        workflow.save()
        try:
            minid = add_minid(user, validated_data['input_minid'])
        except ValueError as ve:
            log.debug(ve)
            raise ValidationError(str(ve))
        first_task = Task(workflow=workflow, user=user,
                          category=tasks[0], status=TASK_READY,
                          name=TASK_METADATA[tasks[0]])
        first_task.save()
        first_task.input.add(minid)

        for t in tasks[1:]:
            tsk = Task(workflow=workflow, user=user, category=t,
                       status=TASK_WAITING, name=TASK_METADATA[t])
            tsk.save()
        return workflow


class WorkspaceSerializer(serializers.HyperlinkedModelSerializer):

    metadata_h = WorkspaceCreateSerializer.metadata_h

    current_task = TaskSerializer(read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    metadata = serializers.JSONField(help_text=metadata_h)

    class Meta:
        model = Workflow
        fields = ('id', 'url', 'date_added', 'metadata', 'current_task',
                  'status', 'tasks')

    validate_metadata = WorkspaceCreateSerializer.validate_metadata
