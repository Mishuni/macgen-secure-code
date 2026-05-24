import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.conf import settings

@csrf_exempt
@require_POST
def create_gif(request):
    try:
        images = request.FILES.getlist('images')
        target_size = request.POST.get('targetSize')
        delay = request.POST.get('delay', 10)
        append_reverted = request.POST.get('appendReverted', 'false').lower() == 'true'

        if not images or not target_size:
            return JsonResponse({'error': 'Missing required parameters.'}, status=400)

        # Validate target size
        if 'x' not in target_size:
            return JsonResponse({'error': 'Invalid target size format.'}, status=400)

        # Validate delay
        try:
            delay = int(delay)
        except ValueError:
            return JsonResponse({'error': 'Invalid delay value.'}, status=400)

        # Save images to temporary files
        temp_files = []
        for image in images:
            if not isinstance(image, InMemoryUploadedFile):
                return JsonResponse({'error': 'Invalid file upload.'}, status=400)
            temp_file_path = os.path.join(settings.BASE_DIR, 'temp', image.name)
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)
            temp_files.append(temp_file_path)

        # Prepare ImageMagick command
        command = ['convert']
        command.extend(temp_files)
        if append_reverted:
            command.extend(reversed(temp_files))
        command.extend(['-resize', target_size, '-delay', str(delay), '-loop', '0', 'gif:-'])

        # Execute command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return JsonResponse({'error': 'Failed to create GIF.'}, status=500)

        # Return GIF
        return HttpResponse(result.stdout, content_type='image/gif')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Clean up temporary files
        for temp_file_path in temp_files:
            try:
                os.remove(temp_file_path)
            except OSError:
                pass