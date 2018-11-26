  /* OSIS stands for Open Student Information System. It's an application
* designed to manage the core business of higher education institutions,
* such as universities, faculties, institutes and professional schools.
* The core business involves the administration of students, teachers,
* courses, programs and so on.
*
* Copyright (C) 2017-2018 Université catholique de Louvain (http://www.uclouvain.be)
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* A copy of this license - GNU General Public License - is available
* at the root of the source code of this program.  If not,
* see http://www.gnu.org/licenses/.
*
* OSIS Custom layout
*/

datatable_options = {
                paging: true,
                lengthChange: true,
                lengthMenu: [ 10, 25, 50, 100, 500, 1000, 2000 ],
                "columnDefs": [ {
                            "targets": 'no-sort',
                            "orderable": false,
                            "searchable": false
                        },
                        {
                            "targets": 'searchable',
                            "orderable": true,
                            "searchable": true,
                            "type": "locale-compare",
                        },
                ],
                "order": [[ 1, "asc" ]],
                "language": {
                    "sProcessing":     gettext('Processing...'),
                    "sSearch":         gettext('Search by name:'),
                    "sLengthMenu":     gettext('Show _MENU_ entries'),
                    "sInfo":           gettext('Showing _START_ to _END_ of _TOTAL_ entries'),
                    "sInfoEmpty":      gettext('Showing 0 to 0 of 0 entries'),
                    "sInfoFiltered":   gettext('(filtered from _MAX_ total entries)'),
                    "sLoadingRecords": gettext('Loading...'),
                    "sZeroRecords":    gettext('No matching records found'),
                    "sEmptyTable":     gettext('No data available in table'),
                    "oPaginate":
                        {
                            "sFirst":      gettext('First'),
                            "sPrevious":   gettext('Previous'),
                            "sNext":       gettext('Next'),
                            "sLast":       gettext('Last'),
                        },
                    "oAria": {
                            "sSortAscending":  gettext(': activate to sort column ascending'),
                            "sSortDescending": gettext(': activate to sort column descending'),
                            }
                },
            };
