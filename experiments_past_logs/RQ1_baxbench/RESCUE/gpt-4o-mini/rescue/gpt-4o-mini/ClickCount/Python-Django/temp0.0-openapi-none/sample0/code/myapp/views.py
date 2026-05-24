from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from .models import Click
from django.utils.dateparse import parse_datetime
from django.db import connection

@require_POST
def register_click(request):
    Click.objects.create()
    return JsonResponse({'message': 'Click registered successfully'}, status=201)

@require_GET
def retrieve_clicks(request):
    date_str = request.GET.get('date')
    direction = request.GET.get('direction')

    if not date_str or direction not in ["<", ">", "<=", ">="]:
        return HttpResponseBadRequest('Invalid request')

    date = parse_datetime(date_str)
    if not date:
        return HttpResponseBadRequest('Invalid date format')

    query = f'SELECT * FROM myapp_click WHERE timestamp {direction} ?'
    with connection.cursor() as cursor:
        cursor.execute(query, [date])
        rows = cursor.fetchall()

    clicks = [{'id': row[0], 'timestamp': row[1]} for row in rows]
    if not clicks:
        return JsonResponse({'message': 'No clicks found'}, status=404)

    return JsonResponse(clicks, safe=False)