from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .models import Message
from django.utils.html import escape
import json

@require_http_methods(["GET", "POST"])
def messages_view(request):
    if request.method == "GET":
        limit = int(request.GET.get("limit", 10))
        offset = int(request.GET.get("offset", 0))
        sort = request.GET.get("sort", "DESC").upper()

        if sort not in ["ASC", "DESC"]:
            return HttpResponseBadRequest("Invalid sort parameter")

        messages = Message.objects.all()
        if sort == "ASC":
            messages = messages.order_by('id')
        else:
            messages = messages.order_by('-id')

        messages = messages[offset:offset + limit]
        response_data = [{"username": msg.username, "content": msg.content} for msg in messages]
        return JsonResponse(response_data, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            content = escape(data.get("content", ""))
            username = escape(data.get("username", ""))
            if not content or not username:
                return HttpResponseBadRequest("Invalid input")

            message = Message.objects.create(content=content, username=username)
            return JsonResponse({"id": message.id}, status=200)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")