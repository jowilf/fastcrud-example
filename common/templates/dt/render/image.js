dt_columns.push({
  data: "{{name}}",
  render: function (data, type, full, meta) {
    if (!data) return null_column()
    if (Array.isArray(data) && data.length == 0) return empty_column();
    if (Array.isArray(data) && type != "display") {
      return data.map((v) => `{{file_url('${v.path}')}}`);
    } else if (type != "display") return `{{file_url('${data.path}')}}`;
    let urls = Array.isArray(data)
      ? data.map((v) => `{{file_url('${v.path}')}}`)
      : [`{{file_url('${data.path}')}}`];
    return `<div class="d-flex">${urls
      .map(
        (url) =>
          `<div class="p-1"><span class="avatar avatar-sm" style="background-image: url(${url})"></span></div>`
      )
      .join("")}</div>`;
  },
});
