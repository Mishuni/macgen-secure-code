from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.html import escape
import json
from .models import Message

@csrf_exempt
def messages_view(request):
    if request.method == 'GET':
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        sort = request.GET.get('sort', 'DESC').upper()

        messages = Message.objects.all().order_by('-created_at' if sort == 'DESC' else 'created_at')
        paginator = Paginator(messages, limit)
        page = paginator.get_page(offset // limit + 1)

        return render(request, 'messages.html', {'messages': page})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = escape(data.get('username', ''))
            content = escape(data.get('content', ''))

            if not username or not content:
                return JsonResponse({'error': 'Invalid input'}, status=400)

            message = Message.objects.create(username=username, content=content)
            return JsonResponse({'id': message.id, 'username': message.username, 'content': message.content}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)