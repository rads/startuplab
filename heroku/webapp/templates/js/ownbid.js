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
$(function() {
    $.ajax({
        url: '/interactions',
        data: {
            id: $('#bidID').attr('data-id'),
        },
        success: function (data) {
            _(data).each(function (interaction) {
                if (interaction.messages.length == 0) {
                    return;
                }
                if (interaction.responder != interaction.messages[0].message) {
                    console.log('fuck');
                }
                var template = _.template($('#message_template').html(), {
                    name: interaction.responder,
                    text: interaction.messages[0].message,
                       
                });
            });
        },
    });
});
