  $('#delete_modal').on('show.bs.modal', (e) => {
      $('#btn-ok').attr('href', $(e.relatedTarget).data('href'));
  });

  $('#pnl_succes_messages').delay(5000).fadeOut(2000);
  $('#pnl_warning_messages').delay(10000).fadeOut(2000);