// setup
$(function () {
    $('#expiretime').datepicker();
    
    
    function set_up_select(tags) {
        $('#tags').select2({
            minimumInputLength: 1,
            tokenSeparators: [',', ';'],
            tags: _.map(tags, function(tag) { return {'id': tag, 'text': tag}; }),
            width: '200px',
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
