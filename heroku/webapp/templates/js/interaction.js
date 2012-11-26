function render_bid(data) {
    var bidview = new BidView({
        model: new BidModel(data[0]),
        el: $('#bid'),
    });
    bidview.render();
}

render_messages = function (data) {
    console.log(data);
    _(data.messages).each(function (message) {
        var msg_html = _.template($('#message_template').html(), {
            name: message.name,
            text: message.msg,
            side: 'right',
            color: 'blue',
        });
        $('#interaction').append(msg_html);
    });
}

$(function () {
    $.ajax({
        url: '/querybids/',
        data:  {
            bidID: $('#bidID').attr('data-id'),
        },
        success: render_bid,
    });
    $.ajax({
        'url': '/bidpages',
        data: {
            id: $('#bidID').attr('data-id'),
        },
        success: render_messages
    });
    $('#respond').click(function (e) {
        $.ajax({
            type: 'POST',
            url: '/reply',
            data: {
                interactionID: $('#interactionID').attr('data-id'),     
                message: $('#response_input').val(),
            },
            success: function (ret) {
                if (ret.success) {
                    var side;
                    $('#interaction').append(_.template($('#message_template').html(), {
                        name: ret.name,
                        text: ret.text,
                        side: 'right',      
                        color: 'blue',
                    }));
                }
            },
        });
    });
});
