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
            color: colors[Math.floor(Math.random()*4)],
            amount: this.model.get('amount'),
        };
        var template = _.template($('#bid_template').html(), vars);
        this.$el.html(template);
    },

});


