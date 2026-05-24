import json
from django.http import JsonResponse
from django.views import View
from .models import Message

class MessageView(View):
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        sort = request.GET.get('sort', 'DESC').upper()

        messages = Message.objects.all()
        if sort == 'ASC':
            messages = messages.order_by('id')
        else:
            messages = messages.order_by('-id')

        messages = messages[offset:offset + limit]
        response_data = [{'content': msg.content, 'username': msg.username} for msg in messages]
        return JsonResponse(response_data, safe=False)

    def post(self, request):
        data = json.loads(request.body)
        message = Message.objects.create(content=data['content'], username=data['username'])
        return JsonResponse({'id': message.id}, status=200)