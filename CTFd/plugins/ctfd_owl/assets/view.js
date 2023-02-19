CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = CTFd.lib.markdown();

CTFd._internal.challenge.preRender = function () { }

CTFd._internal.challenge.render = function (markdown) {
    return CTFd._internal.challenge.renderer.render(markdown);
}

CTFd._internal.challenge.postRender = function () {
    loadInfo();
}

CTFd._internal.challenge.submit = function (preview) {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    var submission = CTFd.lib.$('#challenge-input').val()

    var body = {
        'challenge_id': challenge_id,
        'submission': submission,
    }
    var params = {}
    if (preview) {
        params['preview'] = true
    }

    return CTFd.api.post_challenge_attempt(params, body).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response;
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response;
        }
        return response;
    });
};

function loadInfo () {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val());
    var target = "/plugins/ctfd_owl/container?challenge_id={challenge_id}";
    target = target.replace("{challenge_id}", challenge_id);

    var params = {};

    CTFd.fetch(target, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        console.log(response);
        if (response.success === false) {
            CTFd.lib.$('#owl-panel').html(
                    '<h5 class="card-title">Error</h5>' +
                    '<h6 class="card-subtitle mb-2 text-muted" id="owl-challenge-count-down">' + response.msg + '</h6>'
            );
        }
        else if(response.remaining_time === undefined) {
            CTFd.lib.$('#owl-panel').html(
                    '<h5 class="card-title">Instance Info</h5><hr>' +
                    '<button type="button" class="btn btn-primary card-link" id="owl-button-boot" onclick="CTFd._internal.challenge.boot()">Launch</button>'
            );
        } else {
            var panel_html = '<h5 class="card-title">Instance Info</h5><hr>' +
                    '<h6 class="card-subtitle mb-2 text-muted" id="owl-challenge-count-down">Remaining Time: ' + response.remaining_time + 's</h6>';
            if(response.type === 'http') {
                panel_html += '<p class="card-text">Domain: <br/>' + '<a href="//' + response.domain + '" target="_blank">' + response.domain + '</a></p>';
            } else {
                panel_html += '<p class="card-text">Domain: <br/>' + '<a href="//' + response.ip + ':' + response.port + '" target="_blank">' + response.ip + ':' + response.port + '</a></p>';
            }
            panel_html += '<button type="button" class="btn btn-danger card-link" id="owl-button-destroy" onclick="CTFd._internal.challenge.destroy()">Destroy</button>' +
                          '<button type="button" class="btn btn-success card-link" id="owl-button-renew" onclick="CTFd._internal.challenge.renew()">Renew</button>';
            CTFd.lib.$('#owl-panel').html(panel_html);
            
            if(window.t !== undefined) {
                clearInterval(window.t);
                window.t = undefined;
            }

            function showAuto(){
                const origin = CTFd.lib.$('#owl-challenge-count-down')[0].innerHTML;
                const second = parseInt(origin.split(": ")[1].split('s')[0]) - 1;
                CTFd.lib.$('#owl-challenge-count-down')[0].innerHTML = 'Remaining Time: ' + second + 's';
                if(second < 0) {
                    loadInfo();
                }
            }
            window.t = setInterval(showAuto, 1000);
        }
    });
};

function stopShowAuto () {
    // 窗口关闭时停止循环
    CTFd.lib.$("#challenge-window").on("hide.bs.modal", function(event) {
        clearInterval(window.t);
        window.t = undefined;
    });
}

CTFd._internal.challenge.destroy = function () {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val());
    var target = "/plugins/ctfd_owl/container?challenge_id={challenge_id}";
    target = target.replace("{challenge_id}", challenge_id);
    var body = {};
    var params = {};

    CTFd.lib.$('#owl-button-destroy')[0].innerHTML = "Waiting...";
    CTFd.lib.$('#owl-button-destroy')[0].disabled = true;
    
    CTFd.fetch(target, {
        method: 'DELETE',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if(response.success) {
            loadInfo();
            CTFd.ui.ezq.ezAlert({
                title: "Success",
                body: "Your instance has been destroyed!",
                button: "OK"
            });
            stopShowAuto();
        } else {
            CTFd.lib.$('#owl-button-destroy')[0].innerHTML = "Destroy";
            CTFd.lib.$('#owl-button-destroy')[0].disabled = false;
            CTFd.ui.ezq.ezAlert({
                title: "Fail",
                body: response.msg,
                button: "OK"
            });
        }
    });
};

CTFd._internal.challenge.renew = function () {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    var target = "/plugins/ctfd_owl/container?challenge_id={challenge_id}";
    target = target.replace("{challenge_id}", challenge_id);
    var body = {};
    var params = {};

    CTFd.lib.$('#owl-button-renew')[0].innerHTML = "Waiting...";
    CTFd.lib.$('#owl-button-renew')[0].disabled = true;

    CTFd.fetch(target, {
        method: 'PATCH',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if(response.success) {
            loadInfo();
            CTFd.ui.ezq.ezAlert({
                title: "Success",
                body: "Your instance has been renewed!",
                button: "OK"
            });
        } else {
            CTFd.lib.$('#owl-button-renew')[0].innerHTML = "Renew";
            CTFd.lib.$('#owl-button-renew')[0].disabled = false;
            CTFd.ui.ezq.ezAlert({
                title: "Fail",
                body: response.msg,
                button: "OK"
            });
        }
    });
};

CTFd._internal.challenge.boot = function () {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    var target = "/plugins/ctfd_owl/container?challenge_id={challenge_id}";
    target = target.replace("{challenge_id}", challenge_id);

    var params = {};

    CTFd.lib.$('#owl-button-boot')[0].innerHTML = "Waiting...";
    CTFd.lib.$('#owl-button-boot')[0].disabled = true;

    CTFd.fetch(target, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if(response.success) {
            loadInfo();
            CTFd.ui.ezq.ezAlert({
                title: "Success",
                body: "Your instance has been deployed!",
                button: "OK"
            });
        } else {
            CTFd.lib.$('#owl-button-boot')[0].innerHTML = "Launch";
            CTFd.lib.$('#owl-button-boot')[0].disabled = false;
            CTFd.ui.ezq.ezAlert({
                title: "Fail",
                body: response.msg,
                button: "OK"
            });
        }
    });
};