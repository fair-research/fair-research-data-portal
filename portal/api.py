import json
import logging
from django.http import HttpResponse

from portal.models import Task, Workflow
from portal.workflow import (TASK_RUNNING, TASK_COMPLETE, TASK_READY, \
                             TASK_WAITING)

log = logging.getLogger(__name__)


def _task_list_response(tasks):
    active_tasks = []

    for task in tasks:
        active_tasks.append({
            'id': task.id,
            'status': task.status
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
    tasks = Task.objects.filter(user=request.user)
    for task in tasks:
        task.update()

    #_ready_next_task(list(tasks))
    return _task_list_response(tasks)


def _ready_next_task(tasks):

    for task in tasks:
        if task.status == TASK_COMPLETE:
            pos = tasks.index(task)
            if pos < len(tasks) - 1:
                next_task = tasks[pos+1]
                if next_task.status == TASK_WAITING:
                    next_task.status = TASK_READY
                    output = task.output.all()
                    if not output:
                        log.error('Task {} has no output, cannot start next task'
                                  ''.format(task))
                    else:
                        for out in output:
                            next_task.input.add(out)
                            log.debug('NEXT TASK OUTPUT HAS BEEN SET {}'.format(next_task))
                    next_task.save()