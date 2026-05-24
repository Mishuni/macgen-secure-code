from django.http import JsonResponse
from django.views import View
from .models import Message
import json

class MessageView(View):
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        sort = request.GET.get('sort', 'desc')

        messages = Message.objects.all()
        if sort == 'ASC':
            messages = messages.order_by('id')
        else:
            messages = messages.order_by('-id')

        messages = messages[offset:offset + limit]
        response_data = [{"username": msg.username, "content": msg.content} for msg in messages]
        return JsonResponse(response_data, safe=False, content_type='application/json')

    def post(self, request):
        try:
            data = json.loads(request.body)
            if 'content' not in data or 'username' not in data:
                return JsonResponse({"error": "Invalid input"}, status=400)
            message = Message.objects.create(content=data['content'], username=data['username'])
            return JsonResponse({"id": message.id}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({"error": "Invalid input"}, status=400)