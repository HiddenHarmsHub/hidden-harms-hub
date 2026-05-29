document.addEventListener("DOMContentLoaded", () => {

    if (document.getElementById('task-id') && document.getElementById('task-id').value !== '') {
        showLoadingOverlay();
        let successCallback = function (response) {
            let result = response.data[0];
            let model_type = response.data[1];
            document.getElementById('mse-form').style.display = 'block';
            document.getElementById('results').value = result;
            document.getElementById('model_type').value = model_type;
            if (model_type === 'NPE') {
                let message = '<p>The table shows the results summary. The samples file is available in the download.</p>';
                document.getElementById('results-display').innerHTML = message + createTable(result.split('|')[0]);
            } else {
                document.getElementById('results-display').innerHTML = createTable(result);
            }          
            removeLoadingOverlay();
        }
        let errorCallback = function (response) {
            document.getElementById('mse-form').style.display = 'block';
            document.getElementById('results').value = 'failed';
            document.getElementById('download-button').value = 'Download input data';
            displayError(response.data);
            removeLoadingOverlay();
        }
        taskChecker.pollTaskState(document.getElementById('task-id').value, {successCallback: successCallback, errorCallback: errorCallback});
    }
    
});


let getCSRFToken = function () {
    let cookieValue, cookies, cookie;
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

let createTable = function(data) {
    const lines = data.split('\n');
    const html = ['<table class="results-table"><tbody>'];
    html.push('<tr>');
    const headers = lines[0].split(',');
    for (let tab of headers) {
        html.push(`<th scope="col">${ tab }</th>`);
    }
    html.push('</tr>');
    for (let i = 1; i < lines.length; i += 1) {
        if (lines[i].trim() !== '') {
            html.push('<tr>');
                for (let tab of lines[i].split(',')) {
                    html.push(`<td>${ tab }</td>`);
                }
            html.push('</tr>');
        }
    }
    html.push('</tbody></table>');
    return html.join('');
};

let displayError = function(data) {
    const opening = document.createElement('p');
    opening.textContent = 'Something went wrong while calculating the results. Please try again later.';
    document.getElementById('results-display').appendChild(opening);
    const error = document.createElement('p');
    error.textContent = data.message;
    document.getElementById('results-display').appendChild(error);
    const closing = document.createElement('p');
    closing.textContent = 'The input data can still be downloaded.';
    document.getElementById('results-display').appendChild(closing);
};

let showLoadingOverlay = function() {
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

let removeLoadingOverlay = function() {
    if (document.getElementById('overlay')) {
        document.getElementsByTagName('body')[0].removeChild(document.getElementById('overlay'));
    }
};

let taskChecker = (function () {

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
            fetch('/pollstate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFTOKEN': getCSRFToken(),
                },
                body: JSON.stringify({task_id: taskId}),
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
