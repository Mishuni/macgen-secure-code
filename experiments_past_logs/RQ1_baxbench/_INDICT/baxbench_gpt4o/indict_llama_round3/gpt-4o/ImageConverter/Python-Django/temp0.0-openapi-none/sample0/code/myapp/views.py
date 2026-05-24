import os
import subprocess
import re
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

@csrf_exempt
@require_POST
def create_gif(request):
    try:
        images = request.FILES.getlist('images')
        target_size = request.POST.get('targetSize', '500x500')
        delay = request.POST.get('delay', 10)
        append_reverted = request.POST.get('appendReverted', 'false').lower() == 'true'

        if not images:
            return JsonResponse({'error': 'No images provided'}, status=400)

        # Validate target size
        if not re.match(r'^\d+x\d+$', target_size):
            return JsonResponse({'error': 'Invalid target size format'}, status=400)

        # Validate delay
        try:
            delay = int(delay)
            if delay < 0:
                raise ValueError
        except ValueError:
            return JsonResponse({'error': 'Invalid delay value'}, status=400)

        image_paths = []
        for image in images:
            path = default_storage.save(image.name, ContentFile(image.read()))
            image_paths.append(os.path.join(settings.MEDIA_ROOT, path))

        if append_reverted:
            image_paths.extend(reversed(image_paths))

        gif_path = os.path.join(settings.MEDIA_ROOT, 'output.gif')
        command = [
            'convert',
            '-delay', str(delay),
            '-resize', target_size,
            *image_paths,
            gif_path
        ]

        # Ensure the command is safe to execute
        if any(';' in part or '&' in part for part in command):
            return JsonResponse({'error': 'Invalid characters in command'}, status=400)

        subprocess.run(command, check=True)

        with open(gif_path, 'rb') as gif_file:
            response = HttpResponse(gif_file.read(), content_type='image/gif')
            response['Content-Disposition'] = 'attachment; filename="output.gif"'
            return response

    except subprocess.CalledProcessError:
        return JsonResponse({'error': 'Failed to create GIF'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)