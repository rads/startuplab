// The bid
$(function() {
    bidresults = new BidResults([]);
    resultsview = new BidResultsView({
        collection: bidresults,
        el: $('#feed'),
    });
    refreshWithQuery({ 'bidID': $('#bidID').attr('data-id') });
});

// The responses
(function() {
    $.ajax({
        url: '/interactions',
        data: {
            id: $('#bidID').attr('data-id'),
        },
        success: function (data) {
            _(data).each(function (info) {
                var raw_html = _.template($('#response_template').html(), {
                    name: info.owner,
                    id: info.id,
                });
                $('#interaction').append(raw_html);
                $('#response' + info.id).click(function() {
                    window.location = '/questions/' + $('#bidID').attr('data-id') + info.id;
                });
            });
        },
    });
});
