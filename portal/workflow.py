
import logging
import requests
from django.conf import settings
from concierge.api import bag_stage
import concierge

from globus_portal_framework import (load_globus_access_token,
                                     load_transfer_client)

from portal.globus_genomics import submit_job, check_status
from portal.minid import add_minid

log = logging.getLogger(__name__)


TASK_GLOBUS_GENOMICS = 'GLOBUS_GENOMICS'
TASK_JUPYTERHUB = 'JUPYTERHUB'

TASK_WAITING = 'WAITING'
TASK_READY = 'READY'
TASK_RUNNING = 'RUNNING'
TASK_COMPLETE = 'COMPLETE'
TASK_ERROR = 'ERROR'


TASK_TASK_NAMES = {
    TASK_GLOBUS_GENOMICS: 'Globus Genomics',
    TASK_JUPYTERHUB: 'Jupyterhub'
}

TASK_STATUS_NAMES = {
    TASK_WAITING: 'Waiting',
    TASK_READY: 'Ready',
    TASK_RUNNING: 'Running',
    TASK_COMPLETE: 'Complete',
    TASK_ERROR: 'Error'
}


def resolve_task(task_model):
    CLASSES = {
        TASK_GLOBUS_GENOMICS: GlobusGenomicsTask,
        TASK_JUPYTERHUB: JupyterhubTask
    }
    return CLASSES[task_model.category](task_model)


class TaskException(Exception):
    def __init__(self, code='', message=''):
        """
        :param code: A short string that can be checked against, such as
            'PermissionDenied'
        :param message: A longer string that describes the problem and action
            that should be taken.
        """
        self.code = code or 'UnexpectedError'
        self.message = message or 'There was an error running the Workflow'

    def __str__(self):
        return '{}: {}'.format(self.code, self.message)

    def __repr__(self):
        return str(self)


class Task:

    def __init__(self, task):
        self.task = task

    def start(self):
        raise NotImplemented()

    def stop(self):
        raise NotImplemented()

    def info(self):
        raise NotImplemented()

    @property
    def status(self):
        return self.task.status

    @status.setter
    def status(self, value):
        self.task.status = value
        self.task.save()

    @property
    def data(self):
        return self.task.data

    @data.setter
    def data(self, value):
        self.task.data = value
        self.task.save()


class GlobusGenomicsTask(Task):

    WORKFLOW_ID = 'ark:/57799/b9x70v'

    def start(self):
        if self.status == TASK_READY:
            input = self.task.input.all().first()
            data = self.data
            data['job'] = submit_job(input.id, self.WORKFLOW_ID,
                                     api_key=data['apikey'])
            self.data = data
            log.debug(self.data)
            if not self.data['job'].get('history_id'):
                raise TaskException('ggtaskstartfail',
                                    'No history id returned on start')
            self.status = TASK_RUNNING
            return

    def info(self):
        try:
            if self.status == TASK_RUNNING:

                hist_id = self.data['job'].get('history_id')
                if not hist_id:
                    return

                data = self.data
                data['status'] = check_status(self.data['apikey'], hist_id)
                # log.debug(data['status'])
                self.data = data
                if data['status'].get('minid'):
                    try:
                        minid = add_minid(self.task.user, data['status']['minid'])
                        self.task.output.add(minid)
                        self.status = TASK_COMPLETE
                    except Exception as e:
                        log.error('{}: {}'.format(self.task.user, e))
                        self.status = TASK_ERROR
                return data['status']
        except Exception as e:
            # raise TaskException('Unexpected Error', str(e))
            log.error('User {} had error with task {}'.format(self.task.user,
                                                              self.task.id))
            self.status = TASK_ERROR


class JupyterhubTask(Task):

    def start(self):
        if self.status == TASK_READY:
            token = load_globus_access_token(self.task.user,
                '524361f2-e4a9-4bd0-a3a6-03e365cac8a9')
            input = self.task.input.all()
            if len(input) > 1:
                raise TaskException('badinput', 'More than one Minid '
                                        'given for staging')
            minid = input[0]
            staging_loc = '/{}'.format(
                self.task.user.username.split('@', 1)[0])
            try:
                self.data = bag_stage([minid.id], settings.JUPYTERHUB_STAGING,
                                      token, prefix=staging_loc,
                                      server=settings.CONCIERGE_SERVER)
                self.status = TASK_RUNNING
            except concierge.exc.LoginRequired:
                self.data = {'error': 'Token expired, please login again.'}
            except Exception as e:
                log.exception(e)
                log.error('Failed to start transfer for {}'
                          ''.format(self.task.user))

    def info(self):
        if self.status == TASK_RUNNING:
            update = requests.get(self.data['url']).json()
            self.data = update
            if update.get('status') == 'SUCCEEDED':
                self.status = TASK_COMPLETE
                self.task.output.add(self.task.input.all().first())

    def stop(self):
        pass

    @property
    def output_metadata(self):
        if self.status == TASK_COMPLETE:
            return {'type': 'link',
                    'link': 'https://jupyterhub.fair-research.org',
                    'title': 'Transfer Location'}