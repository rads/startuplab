function populate_default_tags(div) {
    $.ajax({
        url: '/usertags',
        success: function (tags) {
            div.select2({
                tags: tags, 
            });
        },
    });
}


obj = {
    shit: 'fuck'
    f: function () {
        var self = this;
        $.ajax({
            url: '/blah',
            success: function () {
                self.shit = 'new thing'            
            },
        });
    }
}

arr = [1,2,3]



obj2 = {
    blah: 'blah',
    f: function () {
        this.blah = 'sad';
    }

}

obj['shit']



