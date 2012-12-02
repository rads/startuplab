//TODO refactor
function set_up_select(tags) {
    $('#searchtags').select2({
        minimumInputLength: 0,
        tokenSeparators: [',', ';'],
        tags: _(tags).map(function(tag) {return {'id': tag, 'text': tag};}),
        width: '100%',
        
    });
    var perm_tags = ["15-1xx", "15-2xx", "21-1xx", "21-2xx", "Python", "C", "C#"];
    $('#searchtags').select2("data", _(perm_tags).map(function (el) {
        return {
            id: el,
            text: el,
        };
    }));
}

$(function() {
    $.ajax({
        url: '/alltags',
        success: set_up_select,
    });
});
