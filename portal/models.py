import json
from django.db import models
from django.contrib.auth.models import User

from globus_portal_framework.search.models import Minid

from portal.workflow import (WORKFLOW_TASK_NAMES, WORKFLOW_STATUS_NAMES,
                             resolve_task)


WORKFLOW_TASK_CHOICES = [(val, name)
                         for val, name in WORKFLOW_TASK_NAMES.items()]
WORKFLOW_STATUS_CHOICES = [(val, name)
                           for val, name in WORKFLOW_STATUS_NAMES.items()]


class Workflow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input = models.ManyToManyField(Minid, related_name='minid_input',
                                   blank=True)
    output = models.ManyToManyField(Minid, related_name='minid_output',
                                    blank=True)
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=128,
                                choices=WORKFLOW_TASK_CHOICES)
    data_store = models.TextField(blank=True)
    status = models.CharField(max_length=64, choices=WORKFLOW_STATUS_CHOICES)
    description = models.CharField(max_length=128, blank=True)

    @property
    def data(self):
        return json.loads(self.data_store) if self.data_store else {}

    @data.setter
    def data(self, value):
        self.data_store = json.dumps(value) if value else json.dumps({})

    @property
    def task(self):
        return resolve_task(self)

    @property
    def template(self):
        return 'components/task-{}.html'.format(self.category.lower())
