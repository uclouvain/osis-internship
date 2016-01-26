$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

$("input[id^='score_']" ).change(function(event) {
  var target = $(event.target);
  var id = target.attr("id");
  if (typeof id == 'undefined') {
    target = target.parent();
    id = target.attr("id");
  }
  if (typeof id != 'undefined') {
    alert("justification_" + id + ": " + $("#justification_" + id).val(''))
  }
});
