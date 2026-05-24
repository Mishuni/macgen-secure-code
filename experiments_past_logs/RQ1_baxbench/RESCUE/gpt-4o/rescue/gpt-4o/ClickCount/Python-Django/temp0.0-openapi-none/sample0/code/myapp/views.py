from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import Click
import json

@csrf_exempt
def click_handler(request):
    if request.method == 'POST':
        # Register a click
        click = Click.objects.create()
        return JsonResponse({'message': 'Click registered successfully', 'id': click.id}, status=201)

    elif request.method == 'GET':
        # Retrieve clicks
        date = request.GET.get('date')
        direction = request.GET.get('direction')

        if not date or not direction:
            return JsonResponse({'error': 'Invalid request. Date and direction are required.'}, status=400)

        try:
            parsed_date = parse_date(date)
            if not parsed_date:
                raise ValueError("Invalid date format")
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        if direction not in ['<', '<=', '>', '>=']:
            return JsonResponse({'error': 'Invalid direction. Use one of <, <=, >, >=.'}, status=400)

        filter_query = {
            f'timestamp__{direction}': parsed_date
        }
        clicks = Click.objects.filter(**filter_query)

        if not clicks.exists():
            return JsonResponse({'error': 'No clicks found.'}, status=404)

        data = [{'id': click.id, 'timestamp': click.timestamp} for click in clicks]
        return JsonResponse(data, safe=False, status=200)

    return JsonResponse({'error': 'Method not allowed.'}, status=405)