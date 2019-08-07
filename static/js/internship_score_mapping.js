const anchor = location.hash;
const grades = ['A', 'B', 'C', 'D'];

$(`#tabs a[href="${anchor}"]`).tab('show');

if(anchor.indexOf("mapping")!==-1){
    $('#tabs a[href="#mapping"]').tab('show');
    $(`#pills a[href="${anchor}"]`).tab('show');
}

$('.nav-pills li').click(event => {
    $("#activePeriod").val(event.currentTarget.getAttribute('name'));
});

let periodClipboard = [];

function copyPeriodValues(period){
    periodClipboard = [];
    for(let apd of Array(15).keys()){
        periodClipboard[apd] = copyValues(period, apd+1);
    }
}

function pastePeriodValues(period){
    for(let [index, values] of periodClipboard.entries()){
        pasteValues(period, index+1, values);
    }
}

let clipboard = {};
function copyValues(period, apd){
    clipboard = {};
    for(let grade of grades) {
        clipboard[grade] = document.getElementById(`mapping${grade}_${period}_${apd}`).value
    }
    return Object.assign({}, clipboard)
}

function pasteValues(period, apd, values){
    if(!values){
        values = clipboard;
    }
    if(Object.keys(clipboard).length !== 0){
        for(let grade of grades){
            document.getElementById(`mapping${grade}_${period}_${apd}`).value = values[grade];
        }
    }
}

function pillChanged(period){
    $("#activePeriod").val(period);
}

function showButtons(period, apd){
    $(`#btn_${period}_${apd}`).show();
}

function hideButtons(period, apd){
    $(`#btn_${period}_${apd}`).hide();
}