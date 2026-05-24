from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.views import View
from .models import Message
import json

@method_decorator(csrf_exempt, name='dispatch')
class MessageView(View):
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        sort = request.GET.get('sort', 'desc').upper()

        messages = Message.objects.all().order_by('-created_at' if sort == 'DESC' else 'created_at')
        paginator = Paginator(messages, limit)
        page_number = offset // limit + 1
        page_obj = paginator.get_page(page_number)

        return render(request, 'messages.html', {'messages': page_obj})

    def post(self, request):
        try:
            data = json.loads(request.body)
            content = data.get('content')
            username = data.get('username')

            if not content or not username:
                return JsonResponse({'error': 'Invalid input'}, status=400)

            message = Message(content=content, username=username)
            message.save()

            return JsonResponse({'message': 'Message posted successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid input'}, status=400)