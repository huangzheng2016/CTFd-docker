const $ = CTFd.lib.$;

function update_configs(event) {
    event.preventDefault();
    const obj = $(this).serializeJSON();
    const target = "/plugins/ctfd_owl/admin/settings";

    var params = {};

    Object.keys(obj).forEach(function(x) {
      if (obj[x] === "true") {
        params[x] = true;
      } else if (obj[x] === "false") {
        params[x] = false;
      } else {
        params[x] = obj[x];
      }
    });

    CTFd.fetch(target, {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(params)
    })
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        window.location.reload();
      });    
    /*CTFd.api.patch_ctfd_owl_config({}, params).then(_response => {
      window.location.reload();
    });*/
  }
  
  $(() => {
    $(".config-section > form:not(.form-upload)").submit(update_configs);
  });