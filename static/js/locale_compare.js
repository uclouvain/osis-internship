jQuery.extend( jQuery.fn.dataTableExt.oSort, {
  'locale-compare-asc': function ( a, b ) {
     return a.localeCompare(b, 'cs', { sensitivity: 'case' })
  },
  'locale-compare-desc': function ( a, b ) {
     return b.localeCompare(a, 'cs', { sensitivity: 'case' })
  }
})

jQuery.fn.dataTable.ext.type.search['locale-compare'] = function (data) {
	return NeutralizeAccent(data);
}

function NeutralizeAccent(data)
{
  return !data
      ? ''
        : typeof data === 'string'
        ? data
        .replace(/\n/g, ' ')
        .replace(/[éÉěĚèêëÈÊË]/g, 'e')
        .replace(/[šŠ]/g, 's')
        .replace(/[čČçÇ]/g, 'c')
        .replace(/[řŘ]/g, 'r')
        .replace(/[žŽ]/g, 'z')
        .replace(/[ýÝ]/g, 'y')
        .replace(/[áÁâàÂÀ]/g, 'a')
        .replace(/[íÍîïÎÏ]/g, 'i')
        .replace(/[ťŤ]/g, 't')
        .replace(/[ďĎ]/g, 'd')
        .replace(/[ňŇ]/g, 'n')
        .replace(/[óÓ]/g, 'o')
        .replace(/[úÚůŮ]/g, 'u')
        : data
}