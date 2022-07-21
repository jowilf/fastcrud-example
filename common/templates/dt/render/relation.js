//{% set foreign_model = (params.identity | to_model)%}
dt_columns.push({
  data: "{{name}}",
  orderable: false,
  render: function (data, type, full, meta) {
    if (!data) return null_column();
    if (Array.isArray(data) && data.length == 0) return empty_column();
    let fpk = "{{foreign_model.pk()}}";
    if (type != "display")
      return (Array.isArray(data) ? data : [data]).map((v) => v[pk]).join(",");
    return `<div class="d-flex flex-row">${(Array.isArray(data) ? data : [data])
      .map(
        (e) =>
          `<a class='mx-1 btn-link' href="{{ admin_url_for(foreign_model, 'show', '${e[fpk]}') }}"><span class='avatar rounded-circle'>${e[fpk]}</span></a>`
      )
      .join("")}</div>`;
  },
});
