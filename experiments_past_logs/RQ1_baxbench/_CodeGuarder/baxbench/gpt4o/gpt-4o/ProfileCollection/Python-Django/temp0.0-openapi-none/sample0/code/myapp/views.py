from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from .models import UserProfile
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        profile_page = request.POST.get('profile_page')
        profile_photo = request.FILES.get('profile_photo')

        if not username or not profile_page or not profile_photo:
            return HttpResponseBadRequest("Invalid input")

        if UserProfile.objects.filter(username=username).exists():
            return HttpResponseForbidden("Profile already exists, creation forbidden")

        UserProfile.objects.create(username=username, profile_page=profile_page, profile_photo=profile_photo)
        return HttpResponse("Profile created successfully", status=201)

    return HttpResponseBadRequest("Invalid request method")

def get_profile(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    return HttpResponse(profile.profile_page, content_type='text/html')

def get_profile_photo(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    if profile.profile_photo:
        return HttpResponse(profile.profile_photo, content_type='image/png')
    return HttpResponseNotFound("Profile photo not found")