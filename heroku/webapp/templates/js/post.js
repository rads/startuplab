// setup
$(function () {
    $('.date').datepicker();

    function set_up_select(tags) {
        $('#tags').select2({
            minimumInputLength: 0,
            tokenSeparators: [',', ';'],
            tags: _.map(tags, function(tag) { return {'id': tag, 'text': tag}; }),
            placeholder: "Start typing...",
        });
    }

    $.ajax({
        url: '/alltags',
        success: set_up_select,
        type: 'json'
    });
    
    $('#post_form').submit(function (e) {
        e.preventDefault();
        var self=this;
        $.ajax({
            url: '/post',
            method: 'POST',
            data: $(self).serialize(),
            success: function () {
            
            },
        });
        console.log('test');
    });

});

