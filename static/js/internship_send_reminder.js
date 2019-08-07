$(document).on('click', '[data-target="#send_reminder"]', function(){
    $.each($("input[name='selected_student']:checked"), function() {
        $("#selected_students").append(
            '<li>'+$(this).data('student')+'</li>'
        );
    });
    if(!$("#li_send_reminder").hasClass('disabled')){
        $("#send_reminder").modal("show");
    }
});

$("#actions").click(() => {
    $("#li_send_reminder").toggleClass(
        'disabled',
        $("input[name='selected_student']:checked").length<1
    );
});

$("#send_reminder").on("hidden.bs.modal", () => {
    $("#selected_students").empty();
});

function sendReminder(){
    $("#send_reminder_form").submit();
}

$("#id_check_all").click(function() {
    $('input:checkbox.selected_object').not(this).prop('checked', this.checked);
});