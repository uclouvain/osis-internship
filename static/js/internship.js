  $('#delete_modal').on('show.bs.modal', (e) => {
      $('#btn-ok').attr('href', $(e.relatedTarget).data('href'));
  });