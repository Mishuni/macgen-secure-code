from django.http import JsonResponse
from django.views import View
from .models import Message
import json

class MessageView(View):
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        sort = request.GET.get('sort', 'DESC')

        messages = Message.objects.all()
        if sort == 'ASC':
            messages = messages.order_by('id')
        else:
            messages = messages.order_by('-id')

        messages = messages[offset:offset + limit]
        data = [{"username": msg.username, "content": msg.content} for msg in messages]
        return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            message = Message.objects.create(content=data['content'], username=data['username'])
            return JsonResponse({"id": message.id}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({"error": "Invalid input"}, status=400)