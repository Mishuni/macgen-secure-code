from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils.html import escape
import json
from .models import Message

@require_http_methods(["GET", "POST"])
@csrf_protect
def messages(request):
    if request.method == "GET":
        try:
            limit = int(request.GET.get('limit', 10))
            offset = int(request.GET.get('offset', 0))
            sort = request.GET.get('sort', 'DESC').upper()

            if limit <= 0 or offset < 0:
                return HttpResponseBadRequest("Invalid pagination parameters")

            messages = Message.objects.all().order_by('-created_at' if sort == 'DESC' else 'created_at')
            paginator = Paginator(messages, limit)
            page_number = (offset // limit) + 1
            page_obj = paginator.get_page(page_number)

            response_data = [
                {
                    "content": escape(message.content),
                    "username": escape(message.username),
                    "created_at": message.created_at.isoformat()
                }
                for message in page_obj
            ]
            return JsonResponse(response_data, safe=False)
        except ValueError:
            return HttpResponseBadRequest("Invalid pagination parameters")

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            username = data.get('username', '').strip()

            if not content or not username:
                return HttpResponseBadRequest("Invalid input")

            # Additional validation can be added here
            if len(content) > 500 or len(username) > 100:
                return HttpResponseBadRequest("Input too long")

            message = Message.objects.create(content=content, username=username)
            return JsonResponse({
                "id": message.id,
                "content": escape(message.content),
                "username": escape(message.username),
                "created_at": message.created_at.isoformat()
            }, status=200)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")