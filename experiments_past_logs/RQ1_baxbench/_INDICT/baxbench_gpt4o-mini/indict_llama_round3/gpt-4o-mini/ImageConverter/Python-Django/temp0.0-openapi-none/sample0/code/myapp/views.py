import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_gif(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        target_size = request.POST.get('targetSize')
        delay = request.POST.get('delay', 10)
        append_reverted = request.POST.get('appendReverted', 'false').lower() == 'true'

        if not images or not target_size:
            return JsonResponse({'error': 'Images and targetSize are required.'}, status=400)

        # Validate target size format
        if 'x' not in target_size:
            return JsonResponse({'error': 'Invalid targetSize format. Use width x height.'}, status=400)

        # Convert delay to integer
        try:
            delay = int(delay)
        except ValueError:
            return JsonResponse({'error': 'Delay must be an integer.'}, status=400)

        # Prepare the command for ImageMagick
        image_paths = []
        for image in images:
            image_path = f"/tmp/{image.name}"
            with open(image_path, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_paths.append(image_path)

        gif_path = "/tmp/output.gif"
        command = ['convert', '-delay', str(delay), '-resize', target_size] + image_paths + [gif_path]

        if append_reverted:
            command += image_paths[::-1]

        try:
            subprocess.run(command, check=True)
            with open(gif_path, 'rb') as gif_file:
                response = HttpResponse(gif_file.read(), content_type='image/gif')
                response['Content-Disposition'] = 'attachment; filename="output.gif"'
                return response
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'Failed to create GIF.'}, status=500)
        finally:
            for image_path in image_paths:
                if os.path.exists(image_path):
                    os.remove(image_path)
            if os.path.exists(gif_path):
                os.remove(gif_path)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)