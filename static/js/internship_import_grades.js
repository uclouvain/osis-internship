$("#upload-form").submit(() => {
    $("#import-submit").attr("disabled", true);
    $("#loader").show();
});

$('#import-submit').attr('disabled',true);
$('input:file').change(
    function(){
        if ($(this).val()){
            $('#import-submit').removeAttr('disabled');
        }
        else {
            $('#import-submit').attr('disabled',true);
        }
    }
);
