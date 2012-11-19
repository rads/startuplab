function set_up_select(tags) {
    $('#searchtags').select2({
        minimumInputLength: 0,
        tokenSeparators: [',', ';'],
        tags: _(tags).map(function(tag) {return {'id': tag, 'text': tag};}),
        width: '100%',
    });
}

$(function () {
    $.ajax({
        url: '/user',
        type: 'json',
        success: set_up_select,
    });
});
