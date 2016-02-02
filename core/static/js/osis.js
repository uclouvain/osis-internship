$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

/*** Score encoding forms *****************************************************/
$("input[id^='score_']" ).change(function(event) {
  // Get the object that received the event.
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id == 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  // Checks whether the object contains an id.
  if (typeof id != 'undefined') {
    if(target.val() != "")
      $("#justification_" + id).val('');
  }
});

$("select[id^='justification_score_']" ).change(function(event) {
  // Get the object that received the event.
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id == 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  // Checks whether the object contains an id.
  if (typeof id != 'undefined') {
    if(target.val() != "")
      $("#" + id.substring(14)).val('');
  }
});

/*** Double encoding ***/
$("input[id^='double_score_']" ).blur(function(event) {
  // Get the object that received the event.
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id == 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  var enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  var score_draft = Number($("#score_draft_" + enrollmentId).val());

  if (target.val() != score_draft)
    target.css("border", "1px solid #ff0000");
  else
    target.css("border", "1px solid lightgrey");

  var double_justification_field = $("#double_justification_score_"+ enrollmentId);
  var justification_double = double_justification_field.val();
  var justification_draft =  $("#justification_draft_" + enrollmentId).val();

  if (justification_double != justification_draft)
    double_justification_field.css("border", "1px solid #ff0000");
  else
    double_justification_field.css("border", "1px solid lightgrey");

  if(target.val() != "") {
      $("#double_justification_score_" + enrollmentId).val('');
  }
});

$("select[id^='double_justification_score_']" ).blur(function(event) {
  // Get the object that received the event.
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id == 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  var enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  var justification_draft =  $("#justification_draft_" + enrollmentId).val();

  if (target.val() != justification_draft)
    target.css("border", "1px solid #ff0000");
  else
    target.css("border", "1px solid lightgrey");

  if(target.val() != "")
      $("#double_score_" + enrollmentId).val('');
});

/*** Double encoding validation ***/
$("button[id^='take_draft_']").click(function(event) {
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id == 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  var enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  var score_draft = $("#score_draft_"+ enrollmentId).val();
  var justification_draft = $("#justification_draft_"+ enrollmentId).val();
  $("#score_final_show_"+ enrollmentId).html(score_draft);
  $("#score_final_"+ enrollmentId).val(score_draft);
  $("#justification_final_show_"+ enrollmentId).html(justification_draft);
  $("#justification_final_"+ enrollmentId).val(justification_draft);
});

$("button[id^='take_reencoded_']").click(function(event) {
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id == 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  var enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  var score_reencoded = $("#score_reencoded_"+ enrollmentId).val();
  var justification_reencoded = $("#justification_reencoded_"+ enrollmentId).val();
  $("#score_final_show_"+ enrollmentId).html(score_reencoded);
  $("#score_final_"+ enrollmentId).val(score_reencoded);
  $("#justification_final_show_"+ enrollmentId).html(justification_reencoded);
  $("#justification_final_"+ enrollmentId).val(justification_reencoded);
});
/******************************************************************************/
