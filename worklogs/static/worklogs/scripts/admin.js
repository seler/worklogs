start_load_time = new Date();

jQuery(document).ready(function (){
    add_tr_classes();
    update_duration();
});

function add_tr_classes(){
    var re=/id_form-\d+-state/;
    $('select').each(function(index) {
        if(re.test($(this).attr('id'))){
            var state = $(this).find("option[selected=selected]").val();
            $(this).parent().parent().addClass('state-' + state);
        }
    });
}

function update_duration(){
    container = jQuery('.duration');
    container2 = jQuery('.dupation');
    if (container.text()){
        seconds = get_seconds(container);
        end_load_time = new Date();
        seconds += Math.ceil((end_load_time - start_load_time) / 1000);
        var duration = get_duration_display(seconds);
        var dupation = get_dupation_display(seconds);
        container.text(duration);
        container2.text(dupation);
        window.setInterval(function(){
            seconds++;
            var duration = get_duration_display(seconds);
            var dupation = get_dupation_display(seconds);
            container.text(duration);
            container2.text(dupation);
        }, 1000);
    }
}

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
    h = Math.floor(seconds / 3600);
    m = Math.floor(seconds / 60) % 60;
    s = seconds % 60;
    return h + 'h ' + m + 'm ' + s +'s'
}

function get_dupation_display(seconds){
    h = seconds / 3600.;
    return Math.round(h * 1000) / 1000
}
