$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

/*** Score encoding forms *****************************************************/
$("input[id^='num_score_']" ).change(function(event) {
  // Get the object that received the event.
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id == 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }
  var enrollmentId = id.substring(id.lastIndexOf("_") + 1);

  if(target.val() != "") {
    $("#slt_justification_score_" + enrollmentId).val('');
  }
});

$("select[id^='slt_justification_score_']" ).change(function(event) {
  // Get the object that received the event.
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id === 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  // Checks whether the object contains an id.
  if (typeof id !== 'undefined') {
    if(target.val() !== "")
      $("#" + id.substring(14)).val('');
  }
});

/*** Double encoding ***/
$("input[id^='num_double_score_']" ).blur(function(event) {
  // Get the object that received the event.
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id === 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  var enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  var score_draft = Number($("#txt_score_draft_" + enrollmentId).val());

  if (target.val() != score_draft)
    target.css("border", "1px solid #ff0000");
  else
    target.css("border", "1px solid lightgrey");

  var double_justification_field = $("#slt_double_justification_score_"+ enrollmentId);
  var justification_double = double_justification_field.val();
  var justification_draft =  $("#txt_justification_draft_" + enrollmentId).val();

  if (justification_double != justification_draft)
    double_justification_field.css("border", "1px solid #ff0000");
  else
    double_justification_field.css("border", "1px solid lightgrey");

  if(target.val() !== "") {
      $("#slt_double_justification_score_" + enrollmentId).val('');
  }
});

$("select[id^='slt_double_justification_score_']" ).blur(function(event) {
  // Get the object that received the event.
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id === 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  var enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  var justification_draft =  $("#txt_justification_draft_" + enrollmentId).val();

  if (target.val() !== justification_draft)
    target.css("border", "1px solid #ff0000");
  else
    target.css("border", "1px solid lightgrey");

  if(target.val() !== "")
      $("#num_double_score_" + enrollmentId).val('');
});

/*** Double encoding validation ***/
$("button[id^='bt_take_draft_']").click(function(event) {
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id === 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  var enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  var score_draft = $("#txt_score_draft_"+ enrollmentId).val();
  var justification_draft = $("#txt_justification_draft_"+ enrollmentId).val();
  $("#pnl_score_final_show_"+ enrollmentId).html(score_draft);
  $("#hdn_score_final_"+ enrollmentId).val(score_draft);
  $("#pnl_justification_final_show_"+ enrollmentId).html(justification_draft);
  $("#hdn_justification_final_"+ enrollmentId).val(justification_draft);
});

$("button[id^='bt_take_reencoded_']").click(function(event) {
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id === 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  var enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  var score_reencoded = $("#txt_score_reencoded_"+ enrollmentId).val();
  var justification_reencoded = $("#txt_justification_reencoded_"+ enrollmentId).val();
  $("#pnl_score_final_show_"+ enrollmentId).html(score_reencoded);
  $("#hdn_score_final_"+ enrollmentId).val(score_reencoded);
  $("#pnl_justification_final_show_"+ enrollmentId).html(justification_reencoded);
  $("#hdn_justification_final_"+ enrollmentId).val(justification_reencoded);
});
/******************************************************************************/
