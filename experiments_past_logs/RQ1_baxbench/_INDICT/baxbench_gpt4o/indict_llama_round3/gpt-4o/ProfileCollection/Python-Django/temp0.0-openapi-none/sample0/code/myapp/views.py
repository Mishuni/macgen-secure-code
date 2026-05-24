from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.core.files.base import ContentFile
from .models import UserProfile
import re
from django.utils.html import escape

@csrf_protect
def add_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        profile_page = request.POST.get('profile_page')
        profile_photo = request.FILES.get('profile_photo')

        if not username or not profile_page or not profile_photo:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        if not re.match(r'^[\w.@+-]+$', username):
            return JsonResponse({'error': 'Invalid username'}, status=400)

        if UserProfile.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Profile already exists'}, status=403)

        profile = UserProfile(username=username, profile_page=escape(profile_page))
        profile.profile_photo.save(profile_photo.name, ContentFile(profile_photo.read()))
        profile.save()

        return JsonResponse({'message': 'Profile created successfully'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_profile(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    return HttpResponse(profile.profile_page, content_type='text/html')

def get_profile_photo(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    if profile.profile_photo:
        with open(profile.profile_photo.path, 'rb') as photo:
            return HttpResponse(photo.read(), content_type='image/png')
    return JsonResponse({'error': 'Profile photo not found'}, status=404)