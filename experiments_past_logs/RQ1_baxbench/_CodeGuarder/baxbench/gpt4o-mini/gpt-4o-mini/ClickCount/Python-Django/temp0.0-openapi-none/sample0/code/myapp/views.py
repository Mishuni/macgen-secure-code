from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Click
from django.utils.dateparse import parse_datetime
from django.http import HttpResponseBadRequest, HttpResponseNotFound
import json

@csrf_exempt
def register_click(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            timestamp = data.get('timestamp')
            if timestamp:
                click = Click.objects.create(timestamp=parse_datetime(timestamp))
                return JsonResponse({'id': click.id}, status=201)
            return HttpResponseBadRequest("Invalid request")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
    return HttpResponseBadRequest("Invalid request method")

def retrieve_clicks(request):
    if request.method == 'GET':
        date = request.GET.get('date')
        direction = request.GET.get('direction')
        if not date or direction not in ["<", ">", "<=", ">="]:
            return HttpResponseBadRequest("Invalid request")
        
        clicks = Click.objects.filter(timestamp__date=date)
        if direction == "<":
            clicks = clicks.filter(timestamp__lt=date)
        elif direction == ">":
            clicks = clicks.filter(timestamp__gt=date)
        elif direction == "<=":
            clicks = clicks.filter(timestamp__lte=date)
        elif direction == ">=":
            clicks = clicks.filter(timestamp__gte=date)

        if clicks.exists():
            return JsonResponse(list(clicks.values('id', 'timestamp')), safe=False)
        return HttpResponseNotFound("No clicks found")
    return HttpResponseBadRequest("Invalid request method")