htmx.on("htmx:configRequest", function (evt) {
    const match = document.cookie.match(/auth=([^;]+)/);
    if (match)
      evt.detail.headers["authorization"] = "Bearer " + match[1];
  });
  