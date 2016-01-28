$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

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
