from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from .models import Message
import json

@csrf_protect
def messages(request):
    if request.method == 'GET':
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        sort = request.GET.get('sort', 'desc').upper()

        messages = Message.objects.all().order_by('-created_at' if sort == 'DESC' else 'created_at')
        paginator = Paginator(messages, limit)
        page_number = (offset // limit) + 1
        page_obj = paginator.get_page(page_number)

        return render(request, 'messages.html', {'messages': page_obj})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')
            username = data.get('username')

            if not content or not username:
                return HttpResponseBadRequest("Invalid input")

            message = Message(content=content, username=username)
            message.save()

            return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid input")