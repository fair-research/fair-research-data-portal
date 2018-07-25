
import logging
import requests
from concierge.api import stage_bag

from globus_portal_framework import (load_globus_access_token,
                                     load_transfer_client)

from portal.globus_genomics import submit_job, check_status
from portal.minid import add_minid

log = logging.getLogger(__name__)


TASK_GLOBUS_GENOMICS = 'GLOBUS_GENOMICS'
TASK_JUPYTERHUB = 'JUPYTERHUB'
TASK_WES = 'WES'

TASK_WAITING = 'WAITING'
TASK_READY = 'READY'
TASK_RUNNING = 'RUNNING'
TASK_COMPLETE = 'COMPLETE'
TASK_ERROR = 'ERROR'


TASK_TASK_NAMES = {
    # TASK_GLOBUS_GENOMICS: 'Globus Genomics',
    # TASK_JUPYTERHUB: 'Jupyterhub'
    TASK_WES: 'Workflow Execution Service'
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
        TASK_JUPYTERHUB: JupyterhubTask,
        TASK_WES: WesTask
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


class WesTask(Task):

    WES_API = 'https://nihcommonstest.globusgenomics.org/wes/'
    WORKFLOWS = 'workflows'

    def start(self):
        if self.status == TASK_READY:
            input = self.task.input.all().first()
            data = self.data

            url = '{}{}'.format(self.WES_API, self.WORKFLOWS)
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': load_globus_access_token(self.task.user,
                                                          'commons')
            }
            payload = {
                'bwa_index': {
                    'class': 'File', 'path': 'ark:/57799/b91414'
                    },
                    'dbsnp': {
                        'class': 'File', 'path': 'ark:/57799/b9wb0k'
                    },
                    'input_file': {
                        'class': 'File', 'path': input.id
                    },
                    'reference_genome': {
                        'class': 'File', 'path': 'ark:/57799/b9mt4f'
                    }
            }
            r = requests.post(url, headers=headers, json=payload)
            log.debug(r.text)
            data['job_id'] = str(r.text)
            self.data = data
            log.debug(self.data)
            if not self.data.get('job_id'):
                raise TaskException('ggtaskstartfail',
                                    'No history id returned on start')
            self.status = TASK_RUNNING
            return

    def info(self):
        try:
            if self.status == TASK_RUNNING:

                job_id = self.data['job'].get('job_id')
                if not job_id:
                    return

                data = self.data
                url = '{}{}/{}/status'.format(WES_API, WORKFLOWS, job_id)

                headers = {
                    'Authorization': load_globus_access_token(self.task.user,
                                                              'commons')
                }

                data['status'] = requests.get(url, headers=headers)
                # log.debug(data['status'])
                self.data = data
                # if data['status'].get('minid'):
                #     try:
                #         minid = add_minid(self.task.user, data['status']['minid'])
                #         self.task.output.add(minid)
                #         self.status = TASK_COMPLETE
                #     except Exception as e:
                #         log.error('{}: {}'.format(self.task.user, e))
                #         self.status = TASK_ERROR
                return data['status']
        except Exception as e:
            # raise TaskException('Unexpected Error', str(e))
            log.error('User {} had error with task {}'.format(self.task.user,
                                                              self.task.id))
            self.status = TASK_ERROR


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

    STAGING_EP = '5b552e84-7ae7-11e8-9443-0a6d4e044368'

    def start(self):
        if self.status == TASK_READY:
            at = load_globus_access_token(self.task.user, 'auth.globus.org')
            tt = load_globus_access_token(self.task.user,
                                          'transfer.api.globus.org')
            input = self.task.input.all()
            if len(input) > 1:
                raise TaskException('badinput', 'More than one Minid '
                                        'given for staging')
            minid = input[0]
            staging_loc = '/{}'.format(
                self.task.user.username.split('@', 1)[0])
            self.data = stage_bag(minid.id, self.STAGING_EP, at, staging_loc,
                                  transfer_token=tt)
            self.status = TASK_RUNNING
            # self.data = {'error': 'Jupyterhub is not running.'}
            # self.status = TASK_ERROR

            return

    def info(self):
        if self.status == TASK_RUNNING:
            update = requests.get(self.data['url']).json()
            # log.debug(update.json())
            taskids = update.get('transfer_task_ids')
            tc = load_transfer_client(self.task.user)
            task_infos = [tc.get_task(t) for t in taskids]
            statuses = [t['status'] for t in task_infos]
            if all([s == 'SUCCEEDED' for s in statuses]):
                self.status = TASK_COMPLETE