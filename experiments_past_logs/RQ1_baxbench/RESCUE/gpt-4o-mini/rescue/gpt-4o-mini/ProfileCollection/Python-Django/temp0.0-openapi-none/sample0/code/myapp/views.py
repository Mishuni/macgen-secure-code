from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import html

@csrf_exempt
def add_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        profile_page = request.POST.get('profile_page')
        profile_photo = request.FILES.get('profile_photo')

        if UserProfile.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Profile already exists'}, status=403)

        # Sanitize the profile page content
        profile_page = html.escape(profile_page)

        user_profile = UserProfile(username=username, profile_page=profile_page, profile_photo=profile_photo)
        user_profile.save()
        return JsonResponse({'message': 'Profile created successfully'}, status=201)

    return JsonResponse({'error': 'Invalid input'}, status=400)

def get_profile(request, username):
    user_profile = get_object_or_404(UserProfile, username=username)
    return HttpResponse(user_profile.profile_page, content_type='text/html')

def get_profile_photo(request, username):
    user_profile = get_object_or_404(UserProfile, username=username)
    response = HttpResponse(user_profile.profile_photo, content_type='image/png')
    return response