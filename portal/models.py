import logging
import json
from django.db import models
from django.contrib.auth.models import User

from globus_portal_framework.search.models import Minid

from portal.workflow import (TASK_TASK_NAMES, TASK_STATUS_NAMES,
                             resolve_task, TASK_ERROR, TaskException)

log = logging.getLogger(__name__)


TASK_TASK_CHOICES = [(val, name)
                         for val, name in TASK_TASK_NAMES.items()]
TASK_STATUS_CHOICES = [(val, name)
                           for val, name in TASK_STATUS_NAMES.items()]

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    globus_genomics_apikey = models.CharField(max_length=128, blank=True)
    minid_email = models.CharField(max_length=128, blank=True)


class Workflow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    @property
    def tasks(self):
        return Task.objects.filter(workflow=self)


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    input = models.ManyToManyField(Minid, related_name='minid_input',
                                   blank=True)
    output = models.ManyToManyField(Minid, related_name='minid_output',
                                    blank=True)
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=128, choices=TASK_TASK_CHOICES)
    data_store = models.TextField(blank=True)
    status = models.CharField(max_length=64, choices=TASK_STATUS_CHOICES)
    description = models.CharField(max_length=128, blank=True)

    @property
    def data(self):
        return json.loads(self.data_store) if self.data_store else {}

    @data.setter
    def data(self, value):
        self.data_store = json.dumps(value) if value else json.dumps({})


    def update(self):
        try:
            return resolve_task(self).info()
        except TaskException as te:
            log.error(te)
            self.status = TASK_ERROR
            self.save()

    # @property
    # def info(self):
    #     try:
    #         return resolve_task(self).info()
    #     except TaskException as te:
    #         log.error(te)
    #         self.status = TASK_ERROR
    #         self.save()

    def start(self):
        try:
            return resolve_task(self).start()
        except TaskException as te:
            log.error(te)
            self.status = TASK_ERROR
            self.save()

    @property
    def task(self):
        return resolve_task(self)

    @property
    def template(self):
        return 'components/task-{}.html'.format(self.category.lower())
