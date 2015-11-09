# -*- coding: utf-8 -*-
from openerp import http

# class Osis-louvain(http.Controller):
#     @http.route('/osis-louvain/osis-louvain/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/osis-louvain/osis-louvain/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('osis-louvain.listing', {
#             'root': '/osis-louvain/osis-louvain',
#             'objects': http.request.env['osis-louvain.osis-louvain'].search([]),
#         })

#     @http.route('/osis-louvain/osis-louvain/objects/<model("osis-louvain.osis-louvain"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('osis-louvain.object', {
#             'object': obj
#         })
