var BidModel = Backbone.Model.extend({
    
});

var BidResults = Backbone.Collection.extend({
    model: BidModel         
});

var BidView = Backbone.View.extend({
    model: BidModel,
    initialize: function () {
        this.render();
    },
    render: function () {
        var vars = { posttime: this.model.get('posttime')};
        var template = _.template($('#bid_template').html(), vars);
        this.$el.html(template) 
    },

});

var BidResultsView = Backbone.View.extend({

    initialize: function () {
        var self = this;
        this.bidviews = [];
        _(this).bindAll('add');
        this.collection.bind('add', this.add);
    },

    render: function() {
        $(this.el).empty();
        var self = this;
        _(this.bidviews).each(function (bv) { 
            bv.render();
            $(self.el).append(bv.el);
        });
    },

    add: function (bid) {
        var bid_el = $('<div id="#' + bid.get('pk') + '"></div>');
        var bidview = new BidView({
            model: bid,
            el: bid_el,
        });
        this.bidviews.push(bidview);
    }
});

var bidresults = new BidResults([]);
var resultsview = new BidResultsView({
    collection: bidresults,
    el: $('#feed_container'),
});


function refreshWithQuery() {
    $.ajax({
        url: '/querybids',
        method: 'GET',
        type: 'json',
        success: function(django_models) {
            _(django_models).each(function (djbid) {
                var model = new BidModel({
                    title: djbid.fields.title,
                    description: djbid.fields.description,
                    posttime: djbid.fields.posttime,
                    pk: djbid.pk, 
                    tags: djbid.tags,

                });
                resultsview.add(model);
            });
            resultsview.render();
        },
        error: function () { alert("AJAX FAIL"); }
    });
}

$(function() {
    
    refreshWithQuery();

});


