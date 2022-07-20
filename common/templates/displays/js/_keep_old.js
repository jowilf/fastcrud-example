$("#{{name}}").on("change", function () {
  if ($("#{{name}}").get(0).files.length > 0) {
    $("#_keep_old_{{name}}").prop("checked", false);
    $("#_keep_old_{{name}}").prop("disabled", true);
  } else {
    $("#_keep_old_{{name}}").prop("checked", true);
    $("#_keep_old_{{name}}").prop("disabled", false);
  }
});
