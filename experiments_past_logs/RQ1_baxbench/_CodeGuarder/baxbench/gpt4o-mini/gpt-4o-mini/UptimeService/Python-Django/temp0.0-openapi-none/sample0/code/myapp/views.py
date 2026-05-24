from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Service
import json
from django.views import View

@method_decorator(csrf_exempt, name='dispatch')
class HeartbeatView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            service_id = data.get('serviceId')
            token = data.get('token')

            if not service_id or not token:
                return JsonResponse({'error': 'Invalid request payload.'}, status=400)

            service, created = Service.objects.get_or_create(serviceId=service_id, defaults={'token': token})
            if not created and service.token != token:
                return JsonResponse({'error': 'Unauthorized access.'}, status=403)

            service.token = token
            service.save()
            return JsonResponse({'message': 'Heartbeat registered successfully.'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid request payload.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ServicesView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            token = data.get('token')

            if not token:
                return JsonResponse({'error': 'Invalid request payload.'}, status=400)

            services = Service.objects.filter(token=token).values('serviceId', 'last_notification')
            return JsonResponse(list(services), safe=False, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid request payload.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)