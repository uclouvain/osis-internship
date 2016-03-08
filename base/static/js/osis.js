$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

/*** Double encoding ***/


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
