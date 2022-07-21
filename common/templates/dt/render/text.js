dt_columns.push({
  data: "{{name}}",
  searchBuilderType: "{{params.search_builder_type}}",
  render: function (data, type, full, meta) {
    if (!data) return null_column();
    if (Array.isArray(data) && data.length == 0) return empty_column();
    if (type != "display")
      return (Array.isArray(data) ? data : [data]).join(",");
    return `<span class="align-middle d-inline-block text-truncate" data-toggle="tooltip" data-placement="bottom" title='${data}' style="max-width: 30em;">
        ${(Array.isArray(data) ? data : [data]).join(",")}</span>`;
  },
});
