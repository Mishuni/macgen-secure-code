from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import Service

@csrf_exempt
def register_heartbeat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service_id = data['serviceId']
            token = data['token']
            service, created = Service.objects.update_or_create(
                serviceId=service_id,
                defaults={'token': token, 'lastNotification': timezone.now()}
            )
            return JsonResponse({'message': 'Heartbeat registered successfully.'}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request payload.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_services(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data['token']
            services = Service.objects.filter(token=token).values('serviceId', 'lastNotification')
            return JsonResponse(list(services), safe=False, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request payload.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)