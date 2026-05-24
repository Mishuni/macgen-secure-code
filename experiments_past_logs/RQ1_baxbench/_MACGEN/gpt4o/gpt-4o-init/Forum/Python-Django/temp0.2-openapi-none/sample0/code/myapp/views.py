from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.views import View
from .models import Message
import json

class MessageView(View):
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        sort = request.GET.get('sort', 'DESC').upper()

        messages = Message.objects.all().order_by('-created_at' if sort == 'DESC' else 'created_at')
        paginator = Paginator(messages, limit)
        page_number = (offset // limit) + 1
        page_obj = paginator.get_page(page_number)

        response_data = [{'username': msg.username, 'content': msg.content} for msg in page_obj]
        return JsonResponse(response_data, safe=False)

    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            content = data.get('content')
            username = data.get('username')

            if not content or not username:
                return HttpResponseBadRequest("Invalid input")

            Message.objects.create(content=content, username=username)
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid input")