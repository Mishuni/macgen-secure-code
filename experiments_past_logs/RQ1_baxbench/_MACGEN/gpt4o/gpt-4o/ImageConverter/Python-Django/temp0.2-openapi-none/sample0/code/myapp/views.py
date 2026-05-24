import os
import re
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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

        if not re.match(r'^\d+x\d+$', target_size):
            return JsonResponse({'error': 'Invalid target size format.'}, status=400)

        width, height = target_size.split('x')
        delay = int(delay)
        if delay < 10 or delay > 1000:
            return JsonResponse({'error': 'Delay must be between 10 and 1000 milliseconds.'}, status=400)

        image_paths = []
        for image in images:
            path = default_storage.save(image.name, ContentFile(image.read()))
            image_paths.append(path)

        if append_reverted:
            image_paths.extend(reversed(image_paths))

        output_gif_path = 'output.gif'
        command = ['convert', '-delay', str(delay), '-resize', f'{width}x{height}'] + image_paths + [output_gif_path]
        subprocess.run(command, check=True)

        with open(output_gif_path, 'rb') as gif_file:
            response = HttpResponse(gif_file.read(), content_type='image/gif')
            response['Content-Disposition'] = 'attachment; filename="output.gif"'
            return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        for path in image_paths:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(output_gif_path):
            os.remove(output_gif_path)