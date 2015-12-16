# -*- coding: utf-8 -*-
##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    A copy of this license - GNU Affero General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

import openerp
from openerp.osv import osv
from openerp import tools
import os
from openerp.tools import image_resize_image

class res_company(osv.osv):
    _inherit="res.company"
    _name="res.company"

    def init(self, cr):
        img=open(os.path.join(os.path.dirname(__file__), 'static', 'description', 'icon.png'), 'rb') .read().encode('base64')
        cr.execute('UPDATE res_partner SET image=%s WHERE is_company=TRUE', (img,))
        size = (180, None)
        cr.execute('UPDATE res_company SET logo_web=%s', (image_resize_image(img, size),))
