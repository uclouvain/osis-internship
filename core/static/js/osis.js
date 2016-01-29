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

  enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  score_draft = Number($("#score_draft_" + enrollmentId).val());

  if (target.val() != score_draft)
    target.css("border", "1px solid #ff0000");
  else
    target.css("border", "0px");

  double_justification_field = $("#double_justification_score_"+ enrollmentId);
  justification_double = double_justification_field.val();
  justification_draft =  $("#justification_draft_" + enrollmentId).val();

  if (justification_double != justification_draft)
    double_justification_field.css("border", "1px solid #ff0000");
  else
    double_justification_field.css("border", "0px");
});

$("select[id^='double_justification_score_']" ).blur(function(event) {
  // Get the object that received the event.
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id == 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }

  enrollmentId = id.substring(id.lastIndexOf("_") + 1);
  justification_draft =  $("#justification_draft_" + enrollmentId).val();

  if (target.val() != justification_draft)
    target.css("border", "1px solid #ff0000");
  else
    target.css("border", "0px");
});
/******************************************************************************/
