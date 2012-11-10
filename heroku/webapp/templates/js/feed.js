var colors = ['orange', 'blue', 'grey', 'purple'];
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
        var vars = { 
            id: this.model.get('id'),
            title: this.model.get('title'),
            description: this.model.get('description'),
            tagstring: this.model.get('tags').join(', '),
            expire_time_text: this.model.get('expiretime'),
            color: 'blue',
            amount: this.model.get('amount'),
        };
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
        url: '/querybids',
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


