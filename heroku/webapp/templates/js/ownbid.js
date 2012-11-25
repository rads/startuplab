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

