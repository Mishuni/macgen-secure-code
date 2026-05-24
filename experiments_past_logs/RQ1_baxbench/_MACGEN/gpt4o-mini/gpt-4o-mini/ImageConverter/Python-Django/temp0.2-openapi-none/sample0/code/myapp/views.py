import os
import subprocess
import re
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_gif(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        target_size = request.POST.get('targetSize')
        delay = request.POST.get('delay', 10)
        append_reverted = request.POST.get('appendReverted', 'false').lower() == 'true'

        # Validate targetSize format
        if not re.match(r'^\d+x\d+$', target_size):
            return JsonResponse({'error': 'Invalid targetSize format. Use widthxheight.'}, status=400)

        # Validate delay
        try:
            delay = int(delay)
            if not (0 < delay <= 1000):
                raise ValueError("Invalid delay")
        except ValueError:
            return JsonResponse({'error': 'Delay must be an integer between 1 and 1000.'}, status=400)

        # Validate uploaded files
        image_paths = []
        for image in images:
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                return JsonResponse({'error': 'Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.'}, status=400)
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                return JsonResponse({'error': 'File size exceeds 5MB limit.'}, status=400)

            image_path = f'/tmp/{image.name}'
            with open(image_path, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_paths.append(image_path)

        gif_path = '/tmp/output.gif'
        convert_command = ['convert', '-delay', str(delay), *image_paths, gif_path]

        if append_reverted:
            convert_command += ['(', *image_paths[::-1], ')']

        try:
            subprocess.run(convert_command, check=True)
            with open(gif_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='image/gif')
                response['Content-Disposition'] = 'attachment; filename="output.gif"'
                return response
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'Failed to create GIF.'}, status=500)
        finally:
            for image_path in image_paths:
                os.remove(image_path)
            if os.path.exists(gif_path):
                os.remove(gif_path)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)