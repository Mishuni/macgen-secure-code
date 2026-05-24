from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import Service
import json
from django.utils import timezone
import hashlib

@csrf_protect
def register_heartbeat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service_id = data['serviceId']
            token = data['token']

            service, created = Service.objects.get_or_create(serviceId=service_id, defaults={'token': token})
            if not created and service.token != hashlib.sha256(token.encode()).hexdigest():
                return JsonResponse({'error': 'Invalid token'}, status=400)

            service.token = token
            service.last_notification = timezone.now()
            service.save()

            return JsonResponse({'message': 'Heartbeat registered successfully.'}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request payload.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred. Please try again later.'}, status=500)

@csrf_protect
def get_services(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data['token']

            services = Service.objects.filter(token=hashlib.sha256(token.encode()).hexdigest()).values('serviceId', 'last_notification')
            return JsonResponse(list(services), safe=False, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request payload.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred. Please try again later.'}, status=500)