from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Service
import json
import re

@csrf_exempt
def register_heartbeat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service_id = data['serviceId']
            token = data['token']

            # Validate serviceId and token format
            if not re.match("^[a-zA-Z0-9_-]*$", service_id):
                return JsonResponse({'error': 'Invalid serviceId format.'}, status=400)

            # Register or update the heartbeat
            service, created = Service.objects.update_or_create(
                serviceId=service_id,
                defaults={'token': token}
            )
            return JsonResponse({'message': 'Heartbeat registered successfully.'}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request payload.'}, status=400)
        except Exception:
            return JsonResponse({'error': 'Internal server error.'}, status=500)

@csrf_exempt
def get_services(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data['token']

            # Validate token format
            if not re.match("^[a-zA-Z0-9_-]*$", token):
                return JsonResponse({'error': 'Invalid token format.'}, status=400)

            # Check if the token exists
            if not Service.objects.filter(token=token).exists():
                return JsonResponse({'error': 'Unauthorized access.'}, status=403)

            services = Service.objects.filter(token=token).values('serviceId', 'lastNotification')
            return JsonResponse(list(services), safe=False, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request payload.'}, status=400)
        except Exception:
            return JsonResponse({'error': 'Internal server error.'}, status=500)