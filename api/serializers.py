from portal.models import Workflow
from rest_framework import serializers


class WorkspaceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Workflow
        fields = ('id', 'url', 'date_added', 'metadata')
