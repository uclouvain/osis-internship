$(document).on('click', '[data-target="#send_summary"]', function(){
    $.each($("input[name='selected_student']:checked"), function() {
        $("#selected_students").append(
            '<li>'+$(this).data('student')+'</li>'
        );
    });
    if(!$("#li_send_summary").hasClass('disabled')){
        $("#send_summary").modal("show");
    }
});

$("#actions").click(() => {
    $("#li_send_summary").toggleClass(
        'disabled',
        $("input[name='selected_student']:checked").length<1
    );
});

$("#send_summary").on("hidden.bs.modal", () => {
    $("#selected_students").empty();
});

function sendSummary(){
    $("#send_summary_form").submit();
}

$("#id_check_all").click(function() {
    $('input:checkbox.selected_object').not(this).prop('checked', this.checked);
});
