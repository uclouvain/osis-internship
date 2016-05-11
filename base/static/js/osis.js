$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

$("#bt_remove").click(function(event) {
    return confirm("Oui?");
});

function invalidScoreMsg(input,decimal_allowed,message_decimal,message_max_score){
    if (input.value > 20){
        input.setCustomValidity(message_max_score)
    }
    else if (input.value != Math.floor(input.value) && !decimal_allowed){
        input.setCustomValidity(message_decimal)
    }
    else{
         input.setCustomValidity('');
    }
}

function disable_enter(e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) {
        e.preventDefault();
    }
    return false;
}