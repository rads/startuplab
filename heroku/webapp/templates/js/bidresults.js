var BidResultsView = Backbone.View.extend({

    initialize: function () {
        var self = this;
        this.bidviews = [];
        _(this).bindAll('add');
        this.collection.bind('add', this.add);
    },

    render: function() {
        var self = this;
        self.$el.empty();

        _(this.bidviews).each(function (bv) { 
            bv.render();
            $(self.$el).append(bv.$el.html());
        });
    },

    add: function (bid) {
        var bid_el = $('<div id="bid' + bid.get('id') + '"></div>');
        var bidview = new BidView({
            model: bid,
            el: bid_el,
        });
        this.bidviews.push(bidview);
    },
    
});

var bidresults;
var resultsview;


function refreshWithQuery(args) {
    bidresults = new BidResults([]);
    resultsview.bidviews = [];
    resultsview.$el.html("Loading...");
    $.ajax({
        url: '/querybids/',
        method: 'GET',
        data: args,
        success: function(django_models) {
            _(django_models).each(function (djbid) {
                var model = new BidModel({
                    id: djbid.id,
                    title: djbid.title,
                    description: djbid.description,
                    amount: djbid.amount,
                    posttime: djbid.posttime,
                    expiretime: djbid.expiretime,
                    pk: djbid.pk, 
                    tags: djbid.tags,
                    text: djbid.text,
                });
                resultsview.add(model);
            });
            resultsview.render();
        },
        error: function () { console.log('Something went very wrong'); }
    });
}


