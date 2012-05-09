start_load_time = new Date();

jQuery(document).ready(function (){
    container = jQuery('.duration');
    if (container.text()){
        seconds = get_seconds(container);
        end_load_time = new Date();
        seconds += Math.ceil((end_load_time - start_load_time) / 1000);
        var duration = get_duration_display(seconds);
        container.text(duration);
        window.setInterval(function(){
            seconds++;
            var duration = get_duration_display(seconds);
            container.text(duration);
        }, 1000);
    }
});

function get_seconds(object){
    var classes = object.attr('class').split(' ');
    var re = /^d(\d+)s$/ig;
    for (c in classes){
        var match = re.exec(classes[c]);
        if (match){
            return parseInt(match[1]);
        }
    }
}

function get_duration_display(seconds){
    h = Math.floor(seconds / 3600)
    m = Math.floor(seconds / 60) % 60
    s = seconds % 60
    return h + 'h ' + m + 'm ' + s +'s'
}
