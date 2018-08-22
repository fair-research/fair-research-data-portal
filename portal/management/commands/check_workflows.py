import json
import requests
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from globus_portal_framework import load_globus_access_token
from portal.models import Workflow, Task
from portal.workflow import (TASK_JUPYTERHUB, TASK_WES, TASK_READY,
                             TASK_COMPLETE, TASK_WAITING)

from pprint import pprint

GMETA_DOC = 'portal/management/gmeta_ingest_doc.json'
DOWNSAMPLE_DOC = 'portal/management/downsample.json'


class Command(BaseCommand):
    help = 'Make a change to workflows'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set-all-ownership-to-me', dest='me', action='store_true',
            help='Set tasks/workflows ownership to "settings.ME". WARNING: '
                 'This destroys ownership for everything and should only be '
                 'used for testing locally with backed up data.',
        )
        parser.add_argument(
            '--fix', dest='fix', action='store_true',
            help='Fix task and workflow models',
        )
        parser.add_argument(
            '--delete-bad', dest='delete', action='store_true',
            help='Delete bad workflows that don\'t pass checks',
        )

    def handle(self, *args, **options):
        if options.get('me'):
            self.own_all_models()

        if options.get('delete'):
            self.delete_bad_workflows()

        self.check_migrations()

        self.check_workflows()

        if options.get('fix'):
            self.fix()
            self.check_workflows()

    def check_workflows(self):
        workflows = Workflow.objects.all()

        bad_workflows = [w for w in workflows if not self.workflow_passes(w)]
        good_workflows = [w for w in workflows if self.workflow_passes(w)]

        print('{} workflows pass all checks.'.format(len(good_workflows)))
        print('{} workflows DO NOT pass.'.format(len(bad_workflows)))


    def workflow_passes(self, workflow):
        tasks = Task.objects.filter(workflow=workflow)

        if len(tasks) != 2:
            print('Workflow does not have 2 tasks!')
            pprint(tasks)
            return False

        task1, task2 = tasks
        if task1.category != TASK_WES or task2.category != TASK_JUPYTERHUB:
            print('Workspace tasks invalid, not WES and Jupyterhub')
            return False

        if task1.workflow != task2.workflow:
            print('Workspace does not match!')
            return False

        if not task1.input.all().first():
            print('Task {} has no input minid!'.format(task1))
            return False

        w_metadata = list(task1.workflow.metadata.keys())
        w_metadata.sort()
        if w_metadata != ['assignment', 'minid', 'nwdid', 'seq']:
            print('Workflow metadata does not match! {}'.format(w_metadata))
            return False

        return True

    def delete_bad_workflows(self):
        workflows = Workflow.objects.all()
        bad_workflows = [w for w in workflows if not self.workflow_passes(w)]
        for w in bad_workflows:
            print('deleted: {}'.format(w))
            w.delete()

    def get_index_by_minid(self):
        with open(GMETA_DOC) as f:
            index = json.loads(f.read())
        gmap = {c['content']['Argon_GUID']: c['content']
                for c in index['ingest_data']['gmeta']}
        with open(DOWNSAMPLE_DOC) as f:
            downsample = json.loads(f.read())
        dmap = {c['Argon_GUID']: c for c in downsample}
        gmap.update(dmap)
        print('Index Reconds: {}'.format(len(gmap)))
        return gmap

    def fix(self):
        workflows = Workflow.objects.all()
        bad_workflows = [w for w in workflows if not self.workflow_passes(w)]

        index_map = self.get_index_by_minid()
        old = []

        for w in bad_workflows:
            assignment = w.name.split()[0]
            tasks = Task.objects.filter(workflow=w)
            for task in tasks:
                seq = task.name.split()[1]
                minid = task.input.all().first()
                if not minid:
                    print('Task {} Workflow {} has no input minid! Skipping...'
                          .format(task, w))
                    continue
                record = index_map.get(minid.id)
                if not record:
                    print('Task Minid does not match!')
                    pprint(requests.get('https://identifiers.globus.org/' +
                                        minid.id).json())
                    return
                metadata = {
                    'assignment': assignment,
                    'seq': seq,
                    'minid': minid.id,
                    'nwdid': index_map[minid.id]['NWD_ID']
                }
                new_w = Workflow(name='{} Topmed {}'
                                      ''.format(metadata['assignment'],
                                                metadata['seq']),
                                 user=task.user,
                                 metadata=metadata
                                 )
                new_w.save()
                task.workflow = new_w
                task.save()
                tt_status = TASK_READY if task.status == TASK_COMPLETE else TASK_WAITING
                transfer_task = Task(workflow=new_w,
                                     user=task.user,
                                     category=TASK_JUPYTERHUB,
                                     status=tt_status,
                                     name='Transfer to Jupyterhub')
                transfer_task.save()
                if transfer_task.status == TASK_READY:
                    transfer_task.input.add(task.output.all().first())
                print('Added: {} for user {}'.format(new_w.name, new_w.user))

                old.append(w)
        print('deleting old workflows')
        for w in old:
            w.delete()

    def own_all_models(self):
        me = User.objects.filter(username=settings.ME).first()
        for w in Workflow.objects.all():
            w.user = me
            w.save()
        for t in Task.objects.all():
            t.user = me
            t.save()
        print('Set ownership on {} workflows, {} tasks'.format(
            len(Workflow.objects.all()),
            len(Task.objects.all())
        ))







