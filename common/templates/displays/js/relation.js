{% set foreign_model = (params.identity | to_model) %}
{% set fields = foreign_model.search_columns().values() | list %}
$("#{{name}}").select2({
    allowClear: true,
    {% if data%}
    data: {{foreign_model._select2_initial_data(request,data) | tojson | safe}},
    {% endif %}
    ajax: {
    url: "{{ds(foreign_model)}}",
    dataType: 'json',
    data: function (params) {
        where = {
            or: [
            {%for col in fields%}
            {
                {{col}}: {
                    contains: params.term
                }
            },
            {%endfor%}
            ]
        }
        return {
            skip: (params.page|| 0) * 20,
            limit: 20,
            where: JSON.stringify(where)
        };
    },
    processResults: function (data, params) {
        return {
            results: $.map(data.items, function(obj) {
                obj.id = obj.{{pk}};
                return obj;
            }),
            pagination: {
                more: (params.page||0)*20 < data.total
            }
        };
    },
    cache: true
    },
    //placeholder: 'Search for a {{key}}',
    minimumInputLength: 0,
    templateResult: function (item){
    if(!item.{{pk}}) return 'Search...'
    return $(`<span>{%for col in fields %}<strong>{{col}}: </strong>${item['{{col}}']} {%endfor%}</span>`);
    },
    templateSelection: function (item) {
    if(!item.{{pk}}) return 'Search...'
        return $(`<span>{%for col in fields %}<strong>{{col}}: </strong>${item['{{col}}']} {%endfor%}</span>`);
    }

});