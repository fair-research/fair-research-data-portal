import json
import requests
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from globus_portal_framework import load_globus_access_token
from portal.models import Workspace, Task
from portal.workflow import (TASK_JUPYTERHUB, TASK_WES, TASK_READY,
                             TASK_COMPLETE, TASK_WAITING, TASK_TASK_NAMES)

from pprint import pprint

GMETA_DOC = 'portal/management/gmeta_ingest_doc.json'
DOWNSAMPLE_DOC = 'portal/management/downsample.json'
# Expected Metadata for each workspace
EXPECTED_METADATA = ['grouping', 'data_id', 'data_set']
META_UPDATE_SEPT_12 = {
    'assignment': 'grouping',
    'nwdid': 'data_id',
    'seq': 'data_set'
}



class Command(BaseCommand):
    help = 'Make a change to workspaces'

    def add_arguments(self, parser):
        # parser.add_argument(
        #     '--fix', dest='fix', action='store_true',
        #     help='Fix task and workspace models',
        # )
        parser.add_argument(
            '--update-metadata', dest='update_metadata', action='store_true',
            help='Update workspace metadata to new style.'
        )
        parser.add_argument(
            '--dry-run', dest='dry_run', action='store_true',
            help='Do the fix but don\'t apply changes.'
        )
        parser.add_argument(
            '--delete-bad', dest='delete', action='store_true',
            help='Delete bad workspaces that don\'t pass checks',
        )

    def handle(self, *args, **options):

        if options.get('update_metadata'):
            self.update_metadata(options.get('dry_run'))
            return

        if options.get('me'):
            self.own_all_models()

        if options.get('delete'):
            self.delete_bad_workspaces()

        self.check_migrations()

        self.check_workspaces()

        if options.get('fix'):
            self.fix()
            self.check_workspaces()

    def check_workspaces(self):
        workspaces = Workspace.objects.all()

        workspace_errors = [self.check_workspace(w) for w in workspaces]
        bad_workspaces = [bw for bw in workspace_errors if bw != []]
        good_workspaces = len(workspaces) - len(bad_workspaces)
        print('{} workspaces pass all checks.'.format(good_workspaces))
        print('{} workspaces DO NOT pass.'.format(len(bad_workspaces)))

        print('\n')
        pack = zip(workspaces, workspace_errors)
        for workspace, errors in pack:
            if not errors:
                continue
            print('Workspace {}'.format(reverse('workspace-detail',
                                                args=[workspace.id])))
            for task in workspace.tasks:
                print('\tTask: {}'.format(reverse('task-detail',
                                                args=[task.id])))
            for error in errors:
                print('\t{}'.format(error))

    def check_workspace(self, workspace):
        errors = []
        tasks = Task.objects.filter(workspace=workspace)

        for task in tasks:
            if task.category not in TASK_TASK_NAMES.keys():
                errors.append('Task {} Unknown category {}'
                              ''.format(task.id, task.category))

        if len(tasks) == 0:
            errors.append('Workspace has no tasks!')

        if len(tasks) > 0 and not tasks[0].input.all().first():
            errors.append('Task {} has no input minid!'.format(task1))

        wm = workspace.metadata
        for m in EXPECTED_METADATA:
            if not wm.get(m):
                errors.append('Metadata -- missing {}'.format(m))

        for m in wm:
            if m not in EXPECTED_METADATA:
                errors.append('Metadata -- unexpected {}'.format(m))

        return errors

    def delete_bad_workspaces(self):
        workspaces = Workspace.objects.all()
        bad_workspaces = [w for w in workspaces if self.check_workspace(w)]
        for w in bad_workspaces:
            print('deleted: {}'.format(w))
            w.delete()
        else:
            print('No bad workspaces to delete')

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

    def update_metadata(self, dry_run=True):
        print('Updating {} to {}'.format(META_UPDATE_SEPT_12.keys(),
                                         META_UPDATE_SEPT_12.values()))

        workspaces = Workspace.objects.all()
        for workspace in workspaces:
            new_metadata = {}
            for old_key, old_value in workspace.metadata.items():
                if old_key in META_UPDATE_SEPT_12.keys():
                    new_metadata[META_UPDATE_SEPT_12.get(old_key)] = old_value
                elif old_key in META_UPDATE_SEPT_12.values():
                    new_metadata[old_key] = old_value
                elif old_key not in META_UPDATE_SEPT_12.values():
                    print('Deleting {}={}'.format(old_key, old_value))
            workspace.metadata = new_metadata
            if not dry_run:
                workspace.save()

            errors = self.check_workspace(workspace)
            if errors:
                print('new workspace has errors: \n')
                print('\n\t'.join(errors))
