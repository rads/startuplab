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
});


function validate_bid() {
    $('#errors').val(''); 
    return true;   
}
