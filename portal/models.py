import logging
import json
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from globus_portal_framework.search.models import Minid

from portal.workflow import (
    TASK_WAITING, TASK_READY, TASK_RUNNING, TASK_COMPLETE, TASK_ERROR,
    TASK_TASK_NAMES, TASK_STATUS_NAMES,
    resolve_task, TaskException
)

log = logging.getLogger(__name__)


TASK_TASK_CHOICES = [(val, name)
                         for val, name in TASK_TASK_NAMES.items()]
TASK_STATUS_CHOICES = [(val, name)
                           for val, name in TASK_STATUS_NAMES.items()]

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    globus_genomics_apikey = models.CharField(max_length=128, blank=True)
    minid_email = models.CharField(max_length=128, blank=True)


class Workspace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    date_added = models.DateField(auto_now_add=True)
    metadata_store = models.TextField(blank=True)

    @property
    def metadata(self):
        return json.loads(self.metadata_store) if self.metadata_store else {}

    @metadata.setter
    def metadata(self, value):
        self.metadata_store = json.dumps(value) if value else json.dumps({})

    @property
    def tasks(self):
        return Task.objects.filter(workspace=self).order_by('id')

    @property
    def status(self):
        return self.current_task.status

    @property
    def current_task(self):
        cur_task, updated = self.update_task_list()
        return cur_task

    def update_task_list(self, check_running=False):
        tasks = list(self.tasks)
        has_updated = False

        for task in tasks:
            if check_running:
                task.update()
            if task.status in [TASK_READY, TASK_RUNNING, TASK_ERROR]:
                return task, has_updated
            if task.status == TASK_WAITING:
                if settings.AUTO_START_NEXT_TASKS:
                    task.start()
                else:
                    task.status = TASK_READY
                task.save()
                has_updated = True
                return task, has_updated
            if task.status == TASK_COMPLETE:
                # Task is last in the list
                if tasks.index(task) + 1 == len(tasks):
                    return task, has_updated

        log.error('No task is active for workspace {} user {}'
                  ''.format(self.user, self))
        return None, has_updated

    def __str__(self):
        return self.name


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
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
            log.exception(te)
            self.status = TASK_ERROR
            self.save()

    def stop(self):
        try:
            log.debug('Stopping task {}'.format(self.name))
            response = resolve_task(self).stop()
            log.debug('Task Stop response: {}'.format(response))
            return response
        except TaskException as te:
            log.exception(te)
            self.status = TASK_ERROR
            self.save()

    @property
    def task(self):
        return resolve_task(self)

    @property
    def input_metadata(self):
        return self.task.input_metadata

    @property
    def output_metadata(self):
        return self.task.output_metadata

    @property
    def display_category(self):
        return TASK_TASK_NAMES[self.category]

    @property
    def template(self):
        return 'components/task-{}.html'.format(self.category.lower())

    def __str__(self):
        return self.name
