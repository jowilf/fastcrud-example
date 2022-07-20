buttons = [];
export_buttons = [];
export_columns = Array.from(
  { length: Object.keys(columns).length },
  (_, i) => i + 2
);
console.log(export_columns);
if (exportConfig.csv)
  export_buttons.push({
    extend: "csv",
    text: '<i class="fa-solid fa-file-csv"></i> CSV',
    exportOptions: {
      columns: export_columns,
      orthogonal: "export",
    },
  });
if (exportConfig.excel)
  export_buttons.push({
    extend: "excel",
    text: '<i class="fa-solid fa-file-excel"></i> Excel',
    exportOptions: {
      columns: export_columns,
      orthogonal: "export",
    },
  });
if (exportConfig.pdf)
  export_buttons.push({
    extend: "pdf",
    text: '<i class="fa-solid fa-file-pdf"></i> PDF',
    exportOptions: {
      columns: export_columns,
      orthogonal: "export",
    },
  });
if (exportConfig.print)
  export_buttons.push({
    extend: "print",
    text: '<i class="fa-solid fa-print"></i> Print',
    exportOptions: {
      columns: export_columns,
      orthogonal: "export",
    },
  });
if (export_buttons.length > 0)
  buttons.push({
    extend: "collection",
    text: '<i class="fa-solid fa-file-export"></i> Export',
    className: "",
    buttons: export_buttons,
  });
noInputCondition = function (cn) {
  return {
    conditionName: cn,
    init: function (a) {
      a.s.dt.one("draw.dtsb", function () {
        a.s.topGroup.trigger("dtsb-redrawLogic");
      });
    },
    inputValue: function () {},
    isInputValid: function () {
      return !0;
    },
  };
};
if (exportConfig.search_builder)
  buttons.push({
    extend: "searchBuilder",
    text: '<i class="fa-solid fa-filter"></i> Filter',
    config: {
      columns: JSON.parse("{{model.search_columns().keys() | list}}"),
      conditions: {
        bool: {
          false: noInputCondition("False"),
          true: noInputCondition("True"),
          null: noInputCondition("Empty"),
          "!null": noInputCondition("Not Empty"),
        },
      },
      greyscale: true,
    },
  });
if (exportConfig.column_visibility)
  buttons.push({
    extend: "colvis",
    text: 'Column visibility <i class="fa-solid fa-caret-down"></i>',
  });
