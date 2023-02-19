const $ = CTFd.lib.$;

function htmlentities(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function copyToClipboard(event, str) {
    // Select element
    const el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);

    $(event.target).tooltip({
        title: "Copied!",
        trigger: "manual"
    });
    $(event.target).tooltip("show");

    setTimeout(function () {
        $(event.target).tooltip("hide");
    }, 1500);
}

$(".click-copy").click(function (e) {
    copyToClipboard(e, $(this).data("copy"));
})

async function delete_container(user_id) {
    let response = await CTFd.fetch("/plugins/ctfd_owl/admin/containers?user_id=" + user_id, {
		method: "DELETE",
		credentials: "same-origin",
		headers: {
			"Accept": "application/json",
			"Content-Type": "application/json"
		}
    });
    response = await response.json();
    return response;
}

async function renew_container(user_id) {
    let response = await CTFd.fetch("/plugins/ctfd_owl/admin/containers?user_id=" + user_id, {
		method: "PATCH",
		credentials: "same-origin",
		headers: {
			"Accept": "application/json",
			"Content-Type": "application/json"
		}
	});
    response = await response.json();
    return response;
}

$(".delete-container").click(function(e) {
    e.preventDefault();
    var container_id = $(this).attr("container-id");
    var user_id = $(this).attr("user-id");

    var body = "<span>Are you sure you want to delete <strong>Container #{0}</strong>?</span>".format(
        htmlentities(container_id)
    );

    CTFd.ui.ezq.ezQuery({
        title: "Destroy Container",
        body: body,
        success: async function () {
            let response = await delete_container(user_id);
            if (!response.success) {
				CTFd.ui.ezq.ezAlert({
					title: "Error",
					body: "Unknown Error!",
					button: "OK"
				});
			}
            location.reload();
        }
    });
});

$(".renew-container").click(function(e) {
    e.preventDefault();
    var container_id = $(this).attr("container-id");
    var user_id = $(this).attr("user-id");

    var body = "<span>Are you sure you want to renew <strong>Container #{0}</strong>?</span>".format(
        htmlentities(container_id)
    );

    CTFd.ui.ezq.ezQuery({
        title: "Renew Container",
        body: body,
        success: async function () {
            let response = await renew_container(user_id);
            if (!response.success) {
				CTFd.ui.ezq.ezAlert({
					title: "Error",
					body: "Unknown Error!",
					button: "OK"
				});
			}
            location.reload();
        },
    });
});

$('#containers-renew-button').click(function (e) {
    let users = $("input[data-user-id]:checked").map(function () {
        return $(this).data("user-id");
    });
    CTFd.ui.ezq.ezQuery({
        title: "Renew Containers",
        body: `Are you sure you want to renew the selected ${users.length} container(s)?`,
        success: async function () {
            await Promise.all(users.toArray().map((user) => renew_container(user)));
            location.reload();
        }
    });
});

$('#containers-delete-button').click(function (e) {
    let users = $("input[data-user-id]:checked").map(function () {
        return $(this).data("user-id");
    });
    CTFd.ui.ezq.ezQuery({
        title: "Delete Containers",
        body: `Are you sure you want to delete the selected ${users.length} container(s)?`,
        success: async function () {
            await Promise.all(users.toArray().map((user) => delete_container(user)));
            location.reload();
        }
    });
});