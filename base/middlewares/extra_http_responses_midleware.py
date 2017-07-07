from django.http import HttpResponseNotAllowed
from django.template.response import TemplateResponse
from django.utils.deprecation import MiddlewareMixin


class ExtraHttpResponsesMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if isinstance(response, HttpResponseNotAllowed):
            response = TemplateResponse(request=request,
                                        template="method_not_allowed.html",
                                        status=405,
                                        context={})
            response.render()
        return response

