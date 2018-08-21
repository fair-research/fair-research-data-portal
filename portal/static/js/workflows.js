

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
var update_count = 0;
var frozen_tasks = [];


function freeze_task(taskid) {
    frozen_tasks.push(taskid);
}

function unfreeze_task(taskid) {
    frozen_tasks.pop(taskid);
}

function is_frozen(taskid) {
    return frozen_tasks.indexOf(taskid) >= 0
}

function task_metadata(task_metadata) {
    console.log(task_metadata);
    if (task_metadata == null) {
        return '<a>--</a>'
    }
    if (task_metadata.type == 'minid') {
        return '<a target="blank" href=' + task_metadata.link + ' + >' + task_metadata.title + '</a>'
    }
    if (task_metadata.type == 'link') {
        return '<a target="blank" href=' + task_metadata.link + ' + >' + task_metadata.title + '</a>'
    }
}

function update_local_task(task) {
    console.log("UPDATING TASK: ", task)
    task_id = 'div#task-' + task.id;
    button_id = 'button#task-button-' + task.id;
    $(task_id).text(task.status);
    $('div#task-display-category-' + task.id).text(task.display_category);


    $('div#task-input-' + task.id).empty();
    $('div#task-input-' + task.id).append(task_metadata(task.input));

    $('div#task-output-' + task.id).empty();
    $('div#task-output-' + task.id).append(task_metadata(task.output));
    if (task.status == 'READY') {
        $(button_id).prop('disabled', false);
    } else {
        $(button_id).prop('disabled', true);
    }
}

function update_tasks() {

    // Only allow one instance to run
    if (update_count >= 1)
        return

    update_count++;
    $.ajax({
        type: 'POST',
        url: API_TASKS_UPDATE,
        data: {
            'csrfmiddlewaretoken': csrftoken
        },
        success: function (response) {
            response['tasks'].forEach(function(task) {
                if (!is_frozen(task.id)) {
                    update_local_task(task);
                }
                if (task.status == 'RUNNING') {
                    all_tasks_finished = false;
                }
            });

            setTimeout(update_tasks, 2000);

            update_count--;
        },
        error: function(responseData, textStatus, errorCode) {
            console.log('Failed to update tasks.', textStatus, errorCode)
        }
    });
}

function start_task(taskid) {

    task = {
        id: taskid,
        status: 'STARTING'
    }
    update_local_task(task);
    freeze_task(taskid)


    $.ajax({
        type: 'POST',
        url: API_TASK_START,
        data: {
            'csrfmiddlewaretoken': csrftoken,
            'taskid': taskid
        },
        success: function (task) {
            unfreeze_task(taskid);
            update_local_task(task);

            console.log('Task started')

        },
        error: function(responseData, textStatus, errorCode) {
            unfreeze_task(taskid);
            console.log('Failed to start task', textStatus, errorCode)
        }
    });
}

update_tasks();

