from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
import json

@csrf_exempt
def add_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        profile_page = request.POST.get('profile_page')
        profile_photo = request.FILES.get('profile_photo')

        if UserProfile.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Profile already exists'}, status=403)

        profile = UserProfile(username=username, profile_page=profile_page, profile_photo=profile_photo)
        profile.save()
        return JsonResponse({'message': 'Profile created successfully'}, status=201)

    return JsonResponse({'error': 'Invalid input'}, status=400)

def get_profile(request, username):
    try:
        profile = UserProfile.objects.get(username=username)
        return HttpResponse(profile.profile_page, content_type='text/html')
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)

def get_profile_photo(request, username):
    try:
        profile = UserProfile.objects.get(username=username)
        with open(profile.profile_photo.path, 'rb') as photo:
            return HttpResponse(photo.read(), content_type='image/png')
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile photo not found'}, status=404)