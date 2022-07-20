const jsonEditor{{ name | title}} = new JSONEditor(document.getElementById("{{name}}"), {
    mode: "tree",
    modes: ["code", "tree"],
    onChangeText: function (json) {
        $("input[name={{key}}]").val(json);
        //console.log($("input[name={{key}}]").val(json));
    },
},{% if data %}{{(data|safe) if is_form_value else (data|tojson|safe)}}{% endif %});
