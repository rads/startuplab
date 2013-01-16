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
        colors = ['orange', 'blue', 'grey', 'green'];
        var vars = { 
            id: this.model.get('id'),
            title: this.model.get('title'),
            description: this.model.get('description'),
            tagstring: this.model.get('tags').join(', '),
            expire_time_text: this.model.get('expiretime'),
            color: colors[Math.floor(Math.random()*colors.length)],
            amount: this.model.get('amount'),
        };
        var template = _.template($('#bid_template').html(), vars);
        this.$el.html(template);
        
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
            $('#q' + bv.model.id).click(function (e) {
                window.location = '/questions/' + bv.model.id;
            }); 
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

function set_up_select(tags) {
    $('#searchtags').select2({
        minimumInputLength: 0,
        tokenSeparators: [',', ';'],
        tags: _(tags).map(function(tag) {return {'id': tag, 'text': tag};}),
        width: '100%',
        
    });
    $('#searchtags').select2("data", _(tags).map(function (el) {
        return {
            id: el,
            text: el,
        };
    }));
}

init_feed = function() {
    bidresults = new BidResults([]);
    resultsview = new BidResultsView({
        collection: bidresults,
        el: $('#feed'),
    });

    $.ajax({
        url: '/usertags',
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
    
}

init_own_bid = function () {

    // The bid
    bidresults = new BidResults([]);
    resultsview = new BidResultsView({
        collection: bidresults,
        el: $('#feed'),
    });
    refreshWithQuery({ 'bidID': $('#bidID').attr('data-id') });

    // The responses
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
}


function show_error(field_name, error) {
    $('[name=' + field_name + ']').addClass('error');
    $('#errors').html(error);
}


init_post = function () {
    $('.date').datepicker();

        $.ajax({
        url: '/alltags',
        success: set_up_select,
    });
    
    $('#post_form').submit(function (e) {
        e.preventDefault();
        var self=this;
        $.ajax({
            url: '/post/',
            type: 'POST',
            data: $(self).serialize().toString(),
            success: function (data) {
                if (data.success) {
                    window.location = data.redirect;
                } else {
                    show_error(data.error.name, data.error.msg);
                }
            },
        });
    });

}

