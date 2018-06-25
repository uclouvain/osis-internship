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
                    "sProcessing":     gettext('datatable_processing'),
                    "sSearch":         gettext('datatable_search_by_name'),
                    "sLengthMenu":     gettext('datatable_lengthmenu'),
                    "sInfo":           gettext('datatable_info'),
                    "sInfoEmpty":      gettext('datatable_infoempty'),
                    "sInfoFiltered":   gettext('datatable_infofiltered'),
                    "sLoadingRecords": gettext('datatable_loadingrecords'),
                    "sZeroRecords":    gettext('datatable_zerorecords'),
                    "sEmptyTable":     gettext('datatable_emptytable'),
                    "oPaginate":
                        {
                            "sFirst":      gettext('datatable_first'),
                            "sPrevious":   gettext('datatable_previous'),
                            "sNext":       gettext('datatable_next'),
                            "sLast":       gettext('datatable_last'),
                        },
                    "oAria": {
                            "sSortAscending":  gettext('datatable_sortascending'),
                            "sSortDescending": "{% trans 'datatable_sortdescending'%}",
                            }
                },
            };
