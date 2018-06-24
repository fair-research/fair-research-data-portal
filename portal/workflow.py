
from concierge.api import stage_bag

from globus_portal_framework import load_globus_access_token


WORKFLOW_GLOBUS_GENOMICS = 'GLOBUS_GENOMICS'
WORKFLOW_JUPYTERHUB = 'JUPYTERHUB'

WORKFLOW_READY = 'READY'
WORKFLOW_RUNNING = 'RUNNING'
WORKFLOW_COMPLETE = 'COMPLETE'


WORKFLOW_TASK_NAMES = {
    WORKFLOW_GLOBUS_GENOMICS: 'Globus Genomics',
    WORKFLOW_JUPYTERHUB: 'Jupyterhub'
}

WORKFLOW_STATUS_NAMES = {
    WORKFLOW_READY: 'Ready',
    WORKFLOW_RUNNING: 'Running',
    WORKFLOW_COMPLETE: 'Complete'
}


def resolve_task(task_model):
    CLASSES = {
        WORKFLOW_GLOBUS_GENOMICS: GlobusGenomicsTask,
        WORKFLOW_JUPYTERHUB: JupyterhubTask
    }
    return CLASSES[task_model.category](task_model)


class WorkflowException(Exception):
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

    @property
    def data(self):
        return task.data

    @data.setter
    def data(self, value):
        self.task.data = value
        self.task.save()


class GlobusGenomicsTask(Task):
    pass


class JupyterhubTask(Task):

    STAGING_EP = '5abdf86e-8f4e-11e7-aa27-22000a92523b'

    def start(self):
        if self.status == WORKFLOW_READY:
            at = load_globus_access_token(self.task.user, 'auth.globus.org')
            tt = load_globus_access_token(self.task.user,
                                          'transfer.api.globus.org')
            input = self.task.input.all()
            if len(input) > 1:
                raise WorkflowException('badinput', 'More than one Minid '
                                        'given for staging')
            minid = input[0]
            self.data = stage_bag(minid.id, self.STAGING_EP, at, 'test',
                                  transfer_token=tt)
            return
