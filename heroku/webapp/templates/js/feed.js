/// CAUTION: CODE RE-USE
//TODO refactor
function set_up_select(tags) {
    $('#searchtags').select2({
        minimumInputLength: 0,
        tokenSeparators: [',', ';'],
        tags: _(tags).map(function(tag) {return {'id': tag, 'text': tag};}),
        width: '100%',
        
    });
    var tags = ["15-1xx", "15-2xx", "21-1xx", "21-2xx", "Python", "C", "C#"];
    $('#searchtags').select2("data", _(tags).map(function (el) {
        return {
            id: el,
            text: el,
        };
    }));
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
    });

    refreshWithQuery();
    
    $('#searchtags').change(function(event) {
        if ($('#searchtags').val() == '') {
            refreshWithQuery();
        } else {
            var tags = $('#searchtags').val().split(',');
            refreshWithQuery({
                tags: tags
            });
        }
    });
    
});


