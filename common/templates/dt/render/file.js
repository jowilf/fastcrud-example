dt_columns.push({
  data: "{{name}}",
  render: function (data, type, full, meta) {
    if (!data) return null_column();
    if (Array.isArray(data) && data.length == 0) return empty_column();
    if (Array.isArray(data) && type != "display") {
      return data.map((v) => `{{file_url('${v.path}')}}`);
    } else if (type != "display") return `{{file_url('${data.path}')}}`;
    data = Array.isArray(data) ? data : [data];
    return `<div class="d-flex flex-column">${data
      .map(
        (e) =>
          `<a href="{{file_url('${e.path}')}}" class="btn-link">
          <i class="fa-solid fa-fw ${get_file_icon(
            e.content_type
          )}"></i><span class="align-middle d-inline-block text-truncate" data-toggle="tooltip" data-placement="bottom" title="${
            e.filename
          }" style="max-width: 30em;">${e.filename}</span></a>`
      )
      .join("")}</div>`;
  },
});
