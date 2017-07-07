from django.http import HttpResponseNotAllowed
from django.template.response import TemplateResponse


class ExtraHttpResponsesMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, HttpResponseNotAllowed):
            response = TemplateResponse(request, 'method_not_allowed.html', {})
            response.status_code = 405
        return response
