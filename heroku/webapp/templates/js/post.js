function set_up_select(tags) {
    $('#tags').select2({
        minimumInputLength: 0,
        tokenSeparators: [',', ';'],
        tags: _.map(tags, function(tag) { return {'id': tag, 'text': tag}; }),
        placeholder: "Start typing...",
    });
}

function show_error(field_name, error) {
    $('[name=' + field_name + ']').addClass('error');
    $('#errors').html(error);
}


// setup
$(function () {
    $('.date').datepicker();

        $.ajax({
        url: '/alltags',
        success: set_up_select,
        type: 'json'
    });
    
    $('#post_form').submit(function (e) {
        e.preventDefault();
        var self=this;
        $.ajax({
            url: '/post/',
            type: 'POST',
            data: $(self).serialize().toString(),
            success: function (data) {
                if (data.success) {
                    window.location = data.redirect;
                } else {
                    show_error(data.error.name, data.error.msg);
                }
            },
        });
    });

});

