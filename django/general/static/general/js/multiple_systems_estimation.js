// $(function () {
//     $('#mse-form').on('submit', function(event) {
//         event.preventDefault();
//         console.log('Form is submitted');

//         fetch('/multiplesystemsestimation/calculator', {
//             method: 'POST',
//             body: new FormData(this)
//         }).then(function (response) {
//             return response.json();
//         }).then(function (data) {

//             // taskChecker.pollTaskState(data.task_id);
//         });
//     });
// })

csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

getCSRFToken = function () {
    var cookieValue, cookies, cookie;
    cookieValue = null;
    if (document.cookie && document.cookie != '') {
        cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i+=1) {
            cookie = cookies[i].trim();
            if (cookie.indexOf('csrftoken=') === 0) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
};



$(function () {
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        }
      }
    });
    if (document.getElementById('task-id') && document.getElementById('task-id').value !== '') {
        showLoadingOverlay();
        successCallback = function (result) {
            document.getElementById('mse-form').style.display = 'block';
            document.getElementById('results').value = result.data;
            document.getElementById('results-display').textContent = result.data;
            removeLoadingOverlay();
        }
        taskChecker.pollTaskState(document.getElementById('task-id').value, {successCallback: successCallback});
    }
});


showLoadingOverlay = function() {
    if (!document.getElementById('overlay')) {
    const overlay = document.createElement('div');
    overlay.id = 'overlay';
    const spinner_div = document.createElement('div');
    spinner_div.id = 'spinner';
    spinner_div.innerHTML = '<span class="flower-12l-48x48" />';
    overlay.appendChild(spinner_div);
    document.getElementsByTagName('body')[0].appendChild(overlay);
    }
};

removeLoadingOverlay = function() {
    if (document.getElementById('overlay')) {
    document.getElementsByTagName('body')[0].removeChild(document.getElementById('overlay'));
    }
};

var taskChecker = (function () {

    let delay;
    let stop = false;

    return {

        _updateTaskStatus: function (result, taskId, optns) {
            if (result.state === 'SUCCESS' || result.state === 'FAILURE') {
                clearTimeout(delay);
                if (result.state === 'SUCCESS') {
                    // success state
                    if (Object.prototype.hasOwnProperty.call(optns, 'successCallback')) {
                        optns.successCallback(result);
                    }
                } else {
                    // failure state
                    if (Object.prototype.hasOwnProperty.call(optns, 'errorCallback')) {
                        optns.errorCallback(result);
                    }
                }
            } else {
                if (result.state === 'PENDING') {
                    // waiting to start
                    if (Object.prototype.hasOwnProperty.call(optns, 'processingCallback')) {
                        optns.processingCallback('pending');
                    }
                } else {
                    // in progress state
                    if (Object.prototype.hasOwnProperty.call(optns, 'processingCallback')) {
                        optns.processingCallback('in_progress');
                    }
                }
                if (stop === false) {
                    delay = setTimeout(() => {taskChecker._poll(taskId, optns);}, 1000);
                }
            }
        },

        _poll: function (taskId, optns) {
            $.ajax({
                url: '/pollstate',
                type: 'POST',
                data: {task_id: taskId}
            }).then(function (result) {
                taskChecker._updateTaskStatus(result, taskId, optns);
            });
        },

        stopPolling: function () {
            stop = true;
            clearTimeout(delay);
        },

        pollTaskState: function (taskId, optns) {
            stop = false;
            delay = setTimeout(() => {taskChecker._poll(taskId, optns);}, 1000);
        }
    };

}());


