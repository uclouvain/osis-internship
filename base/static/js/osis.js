$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    check_browser();
});

$.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
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
    if (keycode_is_enter(keyCode)) {
        e.preventDefault();
    }
    return false;
}

function keycode_is_enter(keyCode){
    return keyCode === 13;
}

function originalValueChanged(values, id, score, justification) {
    if (score == null || score == "") {
        score = -1;
    } else {
        score = parseFloat(score);
    }

    if (justification == null) justification = '';

    for (i = 0; i < values.length; i++) {
        if (values[i][0] == id) {
            // To test
            //console.log(parseFloat(values[i][1].replace(",", ".")) + " : " + score)
            //console.log(values[i][2] + " : " + justification)
            if(score == parseFloat(values[i][1].replace(",", ".")) && justification == values[i][2]) {
                return false;
            } else {
                return true;
            }
        }
    }
    return null;
}

function check_browser(){
    var browser = get_browser();
    var accepted = false;
    if (browser.name in browser_supported_versions){
        var accepted_version = browser_supported_versions[browser.name];
        console.log(accepted_version);
        console.log(browser.version);
        if (browser.version >= accepted_version) {
            accepted = true;
        }
    }
    if(accepted) {
        $("#alert_wrong_version").hide();
    } else {
        $("#alert_wrong_version").show();
    }
}

function get_browser() {
    var ua=navigator.userAgent,tem,M=ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
    if(/trident/i.test(M[1])){
        tem=/\brv[ :]+(\d+)/g.exec(ua) || [];
        return {name:'ie',version:(tem[1]||'')};
    }
    if(M[1]==='Chrome'){
        tem=ua.match(/\bOPR\/(\d+)/)
        if(tem!=null)   {return {name:'opera', version:tem[1]};}
    }
    M=M[2]? [M[1], M[2]]: [navigator.appName, navigator.appVersion, '-?'];
    if((tem=ua.match(/version\/(\d+)/i))!=null) {M.splice(1,1,tem[1]);}
    return {
        name: M[0].toLowerCase(),
        version: M[1].toLowerCase()
    };
}

var browser_supported_versions = {
    firefox: 46,
    chrome: 50,
    opera: 37,
    ie: 10,
    safari: 8,
    edge: 24
}