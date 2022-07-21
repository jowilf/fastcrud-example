dt_columns.push({
  data: null,
  orderable: false,
  render: function (data, type, full, meta) {
    editButton = ` <a href="{{ admin_url_for(model, 'edit', '${full.DT_RowId}') }}" data-bs-toggle="tooltip" data-bs-placement="top" title="Edit">
    <span class="me-1"><i class="fa-solid fa-edit"></i></span></a>`;

    return `
      <div class="d-flex">
      <a href="{{ admin_url_for(model, 'show', '${
        full.DT_RowId
      }')}}" data-bs-toggle="tooltip" data-bs-placement="top" title="View">
              <span class="me-1"><i class="fa-solid fa-eye"></i></span>
        </a>
       ${can_edit ? editButton : ""}
        <div>
      `;
  },
});
