var Interaction = Backbone.Model.extend({

});


var InteractionView = Backbone.View.extend({
    model: Interaction,

    initialize: function () {
    
    },

    render: function () {
    
    },

});


function render_bid(data) {
    var bidview = new BidView({
        model: new BidModel(data),
        el: $('#bid'),
    });
    bidview.render();
}

function render_interaction(data) {

}

$(function () {
    $.ajax({
        url: '/querybids',
        data:  {
            'bidID': $('#bidID').data('id'),
        },
        success: render_bid,
    });
    $.ajax({
        'url': '',
        data: {
            'type': 'json'
        },
        success: render_interaction
    });
});
