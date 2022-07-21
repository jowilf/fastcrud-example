dt_columns.push({
  data: "{{name}}",
  searchBuilderType: "{{params.search_builder_type}}",
  render: function (data, type, full, meta) {
    if (!data) return null_column();
    if (Array.isArray(data) && data.length == 0) return empty_column();
    let params = columns["{{name}}"];
    if (!params.input_format) params.input_format = moment.defaultFormat;
    if (Array.isArray(data)) {
      data = data.map((v) =>
        moment(v, params.input_format).format(params.output_format)
      );
      if (type == "display")
        return `<span class="align-middle d-inline-block text-truncate" data-toggle="tooltip" data-placement="bottom" title='${JSON.stringify(
          data
        )}' style="max-width: 30em;">${pretty_print_json(data)}</span>`;
      else return data;
    } else
      return `<span>${moment(data, params.input_format).format(
        params.output_format
      )}</span>`;
  },
});
