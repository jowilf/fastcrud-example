a = {
  data: null,
  orderable: false,
  render: function (data, type, full, meta) {
    var is_check = selectedRows.indexOf(full.DT_RowId + "") > -1;
    return `<input data-id="${
      full.DT_RowId
    }" class="form-check-input" type="checkbox" ${is_check ? "checked" : ""}>`;
  },
};
