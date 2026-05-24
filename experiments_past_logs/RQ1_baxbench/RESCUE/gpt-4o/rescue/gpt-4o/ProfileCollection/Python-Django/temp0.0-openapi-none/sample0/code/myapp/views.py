from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from .models import UserProfile
import os

@csrf_exempt
@require_http_methods(["POST"])
def add_profile(request):
    username = request.POST.get('username')
    profile_page = request.POST.get('profile_page')
    profile_photo = request.FILES.get('profile_photo')

    if not username or not profile_page or not profile_photo:
        return JsonResponse({'error': 'Invalid input'}, status=400)

    if UserProfile.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Profile already exists'}, status=403)

    profile_photo_path = default_storage.save(
        f'profile_photos/{username}.png', ContentFile(profile_photo.read())
    )

    UserProfile.objects.create(
        username=username,
        profile_page=profile_page,
        profile_photo=profile_photo_path
    )

    return JsonResponse({'message': 'Profile created successfully'}, status=201)

@require_http_methods(["GET"])
def get_profile(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    return HttpResponse(profile.profile_page, content_type='text/html')

@require_http_methods(["GET"])
def get_profile_photo(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    if not profile.profile_photo:
        raise Http404("Profile photo not found")
    with open(profile.profile_photo.path, 'rb') as photo:
        return HttpResponse(photo.read(), content_type='image/png')