const jsonEditor{{ name | title}} = new JSONEditor(document.getElementById("{{name}}"), {
    mode: "view"
},{% if data %}{{data|tojson|safe}}{% endif %});
