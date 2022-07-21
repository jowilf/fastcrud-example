dt_columns.push({
  data: "{{key}}",
  render: function (data, type, full, meta) {
    if (type != "display") return data;
    if (data) {
      return `<span class="align-middle d-inline-block text-truncate" data-toggle="tooltip" data-placement="bottom" title='${JSON.stringify(
        data
      )}' style="max-width: 30em;">${pretty_print_json(data)}</span>`;
    } else return null_column();
  },
});
