function get_file_icon(mimeType) {
  mapping = {
    image: "fa-file-image",
    audio: "fa-file-audio",
    video: "fa-file-video",
    "application/pdf": "fa-file-pdf",
    "application/msword": "fa-file-word",
    "application/vnd.ms-word": "fa-file-word",
    "application/vnd.oasis.opendocument.text": "fa-file-word",
    "application/vnd.openxmlformatsfficedocument.wordprocessingml":
      "fa-file-word",
    "application/vnd.ms-excel": "fa-file-excel",
    "application/vnd.openxmlformatsfficedocument.spreadsheetml":
      "fa-file-excel",
    "application/vnd.oasis.opendocument.spreadsheet": "fa-file-excel",
    "application/vnd.ms-powerpoint": "fa-file-powerpoint",
    "application/vnd.openxmlformatsfficedocument.presentationml":
      "fa-file-powerpoint",
    "application/vnd.oasis.opendocument.presentation": "fa-file-powerpoint",
    "text/plain": "fa-file-text",
    "text/html": "fa-file-code",
    "text/csv": "fa-file-csv",
    "application/json": "fa-file-code",
    "application/gzip": "fa-file-archive",
    "application/zip": "fa-file-archive",
  };

  for (var key in mapping) {
    if (mimeType.search(key) === 0) {
      return mapping[key];
    }
  }
  return "fa-file";
}
function null_column() {
  return '<span class="text-center text-muted"> {{"-null-"}} </span>';
}
function empty_column() {
  return '<span class="text-center text-muted"> {{"-empty-"}} </span>';
}
function pretty_print_json(data) {
  var jsonLine = /^( *)("[\w]+": )?("[^"]*"|[\w.+-]*)?([,[{])?$/gm;
  var replacer = function (match, pIndent, pKey, pVal, pEnd) {
    var key = '<span class="json-key" style="color: brown">',
      val = '<span class="json-value" style="color: navy">',
      str = '<span class="json-string" style="color: olive">',
      r = pIndent || "";
    if (pKey) r = r + key + pKey.replace(/[": ]/g, "") + "</span>: ";
    if (pVal) r = r + (pVal[0] == '"' ? str : val) + pVal + "</span>";
    return r + (pEnd || "");
  };

  return JSON.stringify(data, null, 3)
    .replace(/&/g, "&amp;")
    .replace(/\\"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(jsonLine, replacer);
}

function extractCriteria(c) {
  console.log("c", c);
  var d = {};
  if ((c.logic && c.logic == "OR") || c.logic == "AND") {
    d[c.logic.toLowerCase()] = [];
    c.criteria.forEach((v) => {
      d[c.logic.toLowerCase()].push(extractCriteria(v));
    });
  } else {
    if (c.type.startsWith("moment-")) {
      api_format = columns[c.data].api_format;
      if (!api_format) api_format = moment.defaultFormat;
      c.value = [];
      if (c.value1) {
        c.value1 = moment(c.value1).format(api_format);
        c.value.push(c.value1);
      }
      if (c.value2) {
        c.value2 = moment(c.value2).format(api_format);
        c.value.push(c.value2);
      }
    }
    cnd = {};
    c_map = {
      "=": "eq",
      "!=": "neq",
      ">": "gt",
      ">=": "ge",
      "<": "lt",
      "<=": "le",
      contains: "contains",
      starts: "startsWith",
      ends: "endsWith",
    };
    if (c.condition == "between") {
      cnd["between"] = c.value;
    }
    else if (c.condition == "!between") {
      cnd["not_between"] = c.value;
    }
    else if (c.condition == "!starts") {
      cnd["not_like"] = `${c.value1}%`;
    } else if (c.condition == "!ends") {
      cnd["not_like"] = `%${c.value1}`;
    } else if (c.condition == "!contains") {
      cnd["not_like"] = `%${c.value1}%`;
    } else if (c.condition == "null") {
      cnd["is"] = null;
    } else if (c.condition == "!null") {
      cnd["is_not"] = null;
    } else if (c.condition == "false") {
      cnd["is"] = false;
    } else if (c.condition == "true") {
      cnd["is"] = true;
    } else if (c_map[c.condition]) {
      cnd[c_map[c.condition]] = c.value1;
    }
    d[c.data] = cnd;
  }
  return d;
}
