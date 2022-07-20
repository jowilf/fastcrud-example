$("#{{name}}").append(pretty_print_json(JSON.parse(`{{data | tojson |safe}}`)));
