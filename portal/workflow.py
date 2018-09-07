import json
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
TASK_WES = 'WES'

TASK_WAITING = 'WAITING'
TASK_READY = 'READY'
TASK_RUNNING = 'RUNNING'
TASK_COMPLETE = 'COMPLETE'
TASK_ERROR = 'ERROR'


TASK_TASK_NAMES = {
    # TASK_GLOBUS_GENOMICS: 'Globus Genomics',
    TASK_JUPYTERHUB: 'Jupyterhub',
    TASK_WES: 'WES'
}

TASK_METADATA = {
    TASK_JUPYTERHUB: {
        'name': 'Jupyterhub',
        'description': 'Transfer to Jupyterhub'
    },
    TASK_WES: {
        'name': 'WES',
        'description': 'Globus Genomics'
    }

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

    @staticmethod
    def minid_metadata(minid):
        if minid:
            return {'type': 'minid', 'link': minid.landing_page,
                    'title': minid.description}
        return None

    @property
    def input_metadata(self):
        return self.minid_metadata(self.task.input.all().first() or None)

    @property
    def output_metadata(self):
        return self.minid_metadata(self.task.output.all().first() or None)


class WesTask(Task):

    WES_API = settings.WES_API
    WORKFLOWS = 'workflows'
    SUBMISSION_JSON = {
    'workflow_descriptor': 'string',
          'workflow_params': {
                'bwa_index':
                    {'class': 'File', 'path': 'ark:/99999/fk4erydOcxk7PA2'},
                'dbsnp':
                    {'class': 'File', 'path': 'ark:/99999/fk4zKBK8XkAnaXQ'},
                'input_file':
                    {'class': 'File', 'path': None},
                'reference_genome':
                    {'class': 'File', 'path': 'ark:/99999/fk4aZVT0ZWH8Ip0'}
          },
          'workflow_type': 'CWL',
          'workflow_type_version': 'v1.0',
          'workflow_url': 'https://github.com/sbg/sbg_dockstore_tools/blob/'
                          'master/topmed-workflows/alignment/'
                          'topmed-alignment.cwl'
    }

    def auth_header(self):
        return {
            'Authorization': load_globus_access_token(self.task.user,
                                                      'commons')
        }

    def start(self):
        if self.status == TASK_READY:
            try:
                input = self.task.input.all().first()
                data = self.data

                url = '{}{}'.format(self.WES_API, self.WORKFLOWS)
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': load_globus_access_token(self.task.user,
                                                              'commons')
                }
                payload = self.SUBMISSION_JSON.copy()
                payload['workflow_params']['input_file']['path'] = input.id
                log.debug('Start sent to {}'.format(url))
                r = requests.post(url, headers=headers, json=payload)
                data['job_id'] = r.json()

                self.data = data
                log.debug(self.data)
                if not self.data.get('job_id'):
                    raise TaskException('ggtaskstartfail',
                                        'No history id returned on start')
                self.status = TASK_RUNNING
                return
            except json.decoder.JSONDecodeError as jde:
                log.exception(jde)
                log.error(
                    'User {} had error with task {}'.format(self.task.user,
                                                            self.task.id))
                self.status = TASK_ERROR
                try:
                    log.debug(r.text)
                except:
                    pass

    def info(self):
        try:
            if self.status == TASK_RUNNING:

                job_id = self.data.get('job_id', {}).get('workflow_id')
                if not job_id:
                    return

                data = self.data
                url = '{}{}/{}'.format(self.WES_API, self.WORKFLOWS, job_id)
                r = requests.get(url, headers=self.auth_header())
                data['status'] = r.json()
                if data['status'].get('state') == 'ok':
                    self.status = TASK_COMPLETE
                    minid = data['status']['outputs']['minid']
                    if not minid:
                        self.status = TASK_ERROR
                    else:
                        model_minid = add_minid(self.task.user, minid)
                        self.task.output.add(model_minid)
                self.data = data
                return data['status']
        except Exception as e:
            log.exception(e)
            log.error('User {} had error with task {}'.format(self.task.user,
                                                              self.task.id))
            self.status = TASK_ERROR
            try:
                log.debug(r.text)
            except:
                pass

    def stop(self):
        if self.status == TASK_RUNNING:
            log.debug(self.data)

            job_id = self.data.get('job_id', {}).get('workflow_id')
            if not job_id:
                return

            data = self.data
            url = '{}{}/{}'.format(self.WES_API, self.WORKFLOWS,
                                   job_id)
            log.debug('Delete sent to {}'.format(url))
            r = requests.delete(url, headers=self.auth_header())
            try:
                data['stop'] = r.json()
            except Exception as e:
                log.error('Task {} for user {} stopped with error'.format(
                    self.task, self.task.user
                ))
                data['stop'] = r.text
                log.debug(r.text)



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