from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Profile
import os

@csrf_exempt
def add_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        profile_page = request.POST.get('profile_page')
        profile_photo = request.FILES.get('profile_photo')

        if not username or not profile_page or not profile_photo:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        if Profile.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Profile already exists'}, status=403)

        if not profile_photo.name.endswith('.png'):
            return JsonResponse({'error': 'Only PNG files are allowed.'}, status=400)

        profile = Profile(username=username, profile_page=profile_page)
        profile.profile_photo.save(profile_photo.name, ContentFile(profile_photo.read()))
        profile.save()

        return JsonResponse({'message': 'Profile created successfully'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_profile(request, username):
    profile = get_object_or_404(Profile, username=username)
    return HttpResponse(profile.profile_page, content_type='text/html')

def get_profile_photo(request, username):
    profile = get_object_or_404(Profile, username=username)
    if profile.profile_photo:
        with open(profile.profile_photo.path, 'rb') as photo:
            return HttpResponse(photo.read(), content_type='image/png')
    return JsonResponse({'error': 'Profile photo not found'}, status=404)