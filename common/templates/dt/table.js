var table = $("#dt").DataTable({
  dom: "PlBfrtip",
  paging: true,
  lengthChange: true,
  searching: false,
  info: true,
  colReorder: true,
  // responsive: true,
  serverSide: true,
  scrollX: true,
  lengthMenu: [
    [5, 10, 25, 50, 100, -1],
    [5, 10, 25, 50, 100, "All"],
  ],
  pagingType: "full_numbers",
  pageLength: 5,
  select: {
    style: "multi",
    selector: "td:first-child .form-check-input",
    className: "row-selected",
  },
  buttons: buttons,
  language: {
    info: "Showing <strong>_START_</strong> to <strong>_END_</strong> off <strong>_TOTAL_</strong> records",
    infoEmpty: "No records available",
    infoFiltered: "",
    searchBuilder: {
      button: {
        _: '<i class="fa-solid fa-filter"></i> Filter (%d)',
      },
    },
  },
  ajax: function (data, callback, settings) {
    order = [];
    data.order.forEach((o) => {
      const { column, dir } = o;
      order.push(`${data.columns[column].data} ${dir}`);
    });
    where = {};
    if (data.searchBuilder && !jQuery.isEmptyObject(data.searchBuilder)) {
      where = extractCriteria(data.searchBuilder);
      console.log(where);
    }
    $.ajax({
      url: "{{ ds(model)}}",
      type: "get",
      headers: JSON.parse(`{{ajax_headers() | tojson | safe}}`),
      data: {
        skip: settings._iDisplayStart,
        limit: settings._iDisplayLength,
        where: JSON.stringify(where),
        order_by: order,
      },
      traditional: true,
      dataType: "json",
      success: function (data, status, xhr) {
        total = data.total;
        data = data.items;
        data.forEach((d) => {
          d.DT_RowId = d[pk];
        });
        callback({
          recordsFiltered: total,
          data: data,
        });
      },
    });
  },
  columns: dt_columns,
  order: [[2, "asc"]],
});

table.buttons().container().appendTo("#dt_wrapper");

table
  .on("select", function (e, dt, type, indexes) {
    var rowData = table.rows(indexes).data().toArray();
    selectedRows = table.rows({ selected: true }).ids().toArray();
    console.log("select", selectedRows);
    if (table.rows({ selected: true }).count() == 0)
      $("#multi-delete-btn").hide();
    else $("#multi-delete-btn").show();
    $("#multi-delete-btn span").text(table.rows({ selected: true }).count());
  })
  .on("deselect", function (e, dt, type, indexes) {
    var rowData = table.rows(indexes).data().toArray();
    selectedRows = table.rows({ selected: true }).ids().toArray();
    console.log("deselect ", selectedRows);
    if (table.rows({ selected: true }).count() == 0)
      $("#multi-delete-btn").hide();
    else $("#multi-delete-btn").show();
    $("#multi-delete-btn span").text(table.rows({ selected: true }).count());
  });

$("#modal-delete-btn").click(function () {
  $("#modal-delete").modal("hide");
  $("#modal-loading").modal("show");
  var where = JSON.stringify({
    pk: { in: selectedRows },
  });
  fetch(`{{ ds(model)}}?where=${where}`, {
    method: "DELETE",
    headers: JSON.parse(`{{ajax_headers() | tojson | safe}}`),
  })
    .then(async (response) => {
      if (response.ok) {
        await new Promise((r) => setTimeout(r, 500));
        $("#modal-loading").modal("hide");
        table.ajax.reload();
        $("#multi-delete-btn").hide();
      } else return Promise.reject();
    })
    .catch(async (error) => {
      await new Promise((r) => setTimeout(r, 500));
      $("#modal-loading").modal("hide");
      $("#modal-error").modal("show");
    });
});

$("#multi-delete-btn").click(function () {
  $("#modal-delete-body span").text(
    table.rows({ selected: true }).count() + " {{model.get_name()}}"
  );
  $("#modal-delete").modal("show");
});
