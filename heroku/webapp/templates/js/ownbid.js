/// CAUTION: CODE RE-USE
//TODO refactor
function set_up_select(tags) {
    $('#searchtags').select2({
        minimumInputLength: 0,
        tokenSeparators: [',', ';'],
        tags: _(tags).map(function(tag) {return {'id': tag, 'text': tag};}),
        width: '100%',
    });
}

$(function() {
    bidresults = new BidResults([]);
    resultsview = new BidResultsView({
        collection: bidresults,
        el: $('#feed'),
    });

   // TODO populate tag bar with user's profile tags
    $.ajax({
        url: '/alltags',
        success: set_up_select,
        type: 'json',
    });

    refreshWithQuery({ 'bidID': $('#bidID').attr('data-id') });
});


