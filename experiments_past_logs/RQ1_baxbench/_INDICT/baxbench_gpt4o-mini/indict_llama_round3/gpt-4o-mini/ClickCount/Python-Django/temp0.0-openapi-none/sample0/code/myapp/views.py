from django.http import JsonResponse
from django.views import View
from .models import Click
from django.utils import timezone
import datetime

class ClickView(View):
    def post(self, request):
        click = Click.objects.create()
        return JsonResponse({'id': click.id, 'timestamp': click.timestamp.isoformat()}, status=201)

    def get(self, request):
        date_str = request.GET.get('date')
        direction = request.GET.get('direction')

        if not date_str or direction not in ["<", ">", "<=", ">="]:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        try:
            date = datetime.datetime.fromisoformat(date_str)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        if direction == "<":
            clicks = Click.objects.filter(timestamp__lt=date)
        elif direction == ">":
            clicks = Click.objects.filter(timestamp__gt=date)
        elif direction == "<=":
            clicks = Click.objects.filter(timestamp__lte=date)
        elif direction == ">=":
            clicks = Click.objects.filter(timestamp__gte=date)

        response_data = [{'id': click.id, 'timestamp': click.timestamp.isoformat()} for click in clicks]
        return JsonResponse(response_data, safe=False, status=200) if clicks.exists() else JsonResponse({'error': 'No clicks found'}, status=404)