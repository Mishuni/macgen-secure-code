from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Profile
from django.core.files.storage import FileSystemStorage
import re

@csrf_exempt
def add_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        profile_page = request.POST.get('profile_page')
        profile_photo = request.FILES.get('profile_photo')

        # Validate username
        if Profile.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Profile already exists'}, status=403)

        # Sanitize profile_page
        allowed_tags = ['b', 'i', 'u', 'a']
        profile_page = re.sub(r'<(?!/?(?:' + '|'.join(allowed_tags) + r')\b)[^>]*>', '', profile_page)

        # Validate profile_photo
        if not profile_photo.name.endswith('.png'):
            return JsonResponse({'error': 'Invalid file type'}, status=400)

        fs = FileSystemStorage()
        fs.save(profile_photo.name, profile_photo)

        profile = Profile(username=username, profile_page=profile_page, profile_photo=profile_photo)
        profile.save()
        return JsonResponse({'message': 'Profile created successfully'}, status=201)

def get_profile(request, username):
    try:
        profile = Profile.objects.get(username=username)
        return HttpResponse(profile.profile_page, content_type='text/html')
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)

def get_profile_photo(request, username):
    try:
        profile = Profile.objects.get(username=username)
        with open(profile.profile_photo.path, 'rb') as photo:
            return HttpResponse(photo.read(), content_type='image/png')
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile photo not found'}, status=404)