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
            tags: this.model.get('tags'),
            expiretime: this.model.get('expiretime'),
            title: this.model.get('title'),
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
        $(this.el).empty();
        var self = this;
        _(this.bidviews).each(function (bv) { 
            bv.render();
            $(self.el).append(bv.el);
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



var bidresults = new BidResults([]);
var resultsview = new BidResultsView({
    collection: bidresults,
    el: $('#feed_container'),
});


function refreshWithQuery(args) {
    //TODO(nikolai) figure out how to remove things from backbone views properly
    bidresults = new BidResults([]);
    resultsview.bidviews = [];
    $('#feed_container').html('');

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
                    // TODO add post time to bid everywhere    posttime: djbid.posttime,
                    expiretime: djbid.expiretime,
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

/// CAUTION: CODE RE-USE
//TODO refactor
function set_up_select(tags) {
    $('#searchtags').select2({
        minimumInputLength: 0,
        tokenSeparators: [',', ';'],
        tags: _(tags).map(function(tag) {return{'id': tag, 'text': tag};}),
        width: '200px',
    });
}

$(function() {
    // TODO populate tag bar with user's profile tags
    $.ajax({
        url: '/alltags',
        success: set_up_select,
        type: 'json',

    });
    refreshWithQuery();
    $('button#search').click(function(event) {
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


