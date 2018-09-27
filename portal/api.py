import json
import logging
from django.http import HttpResponse

from portal.models import Task, Workspace
from portal.workflow import (TASK_RUNNING, TASK_COMPLETE, TASK_READY, \
                             TASK_WAITING)

log = logging.getLogger(__name__)


def _task_list_response(tasks):
    active_tasks = []

    for task in tasks:
        active_tasks.append({
            'id': task.id,
            'status': task.status,
            'display_category': task.display_category,
            'input': task.input_metadata,
            'output': task.output_metadata,
        })

    response_data = json.dumps({
        'tasks': active_tasks
    })
    return HttpResponse(response_data, content_type="application/json")


def task_start(request):
    tasks = []
    if request.method == 'POST':
        taskid = request.POST.get('taskid')
        task = Task.objects.filter(user=request.user, id=taskid).first()
        if task and task.input.all():
            log.debug(task.status)
            task.start()
            log.debug(task.status)
            log.debug(Task.objects.filter(user=request.user, id=taskid).first().status)
            tasks.append(task)
    return _task_list_response(tasks)


def update_tasks(request):
    for w in Workspace.objects.filter(user=request.user):
        w.update_task_list(check_running=True)
    # The frontend requires the last task too, so give it all of them.
    return _task_list_response(Task.objects.filter(user=request.user))
