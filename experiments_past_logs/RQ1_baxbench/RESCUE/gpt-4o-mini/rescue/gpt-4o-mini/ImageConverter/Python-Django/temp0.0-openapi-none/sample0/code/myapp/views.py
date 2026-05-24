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

        # Validate target size
        if not target_size or 'x' not in target_size:
            return JsonResponse({'error': 'Invalid target size format. Use width x height.'}, status=400)

        # Validate delay
        try:
            delay = int(delay)
        except ValueError:
            return JsonResponse({'error': 'Delay must be an integer.'}, status=400)

        # Validate images
        if not images:
            return JsonResponse({'error': 'No images provided.'}, status=400)

        # Create a temporary directory for images
        temp_dir = 'temp_images'
        os.makedirs(temp_dir, exist_ok=True)

        try:
            image_paths = []
            for image in images:
                # Save the uploaded images
                image_path = os.path.join(temp_dir, image.name)
                with open(image_path, 'wb+') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
                image_paths.append(image_path)

            # Prepare the command for ImageMagick
            gif_name = 'output.gif'
            command = ['convert'] + image_paths + ['-delay', str(delay), '-loop', '0', gif_name]

            # Append reverted images if requested
            if append_reverted:
                command += image_paths[::-1]

            # Execute the command
            subprocess.run(command, check=True)

            # Serve the generated GIF
            with open(gif_name, 'rb') as gif_file:
                response = HttpResponse(gif_file.read(), content_type='image/gif')
                response['Content-Disposition'] = 'attachment; filename="output.gif"'
                return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            # Clean up temporary files
            for image_path in image_paths:
                if os.path.exists(image_path):
                    os.remove(image_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            if os.path.exists(gif_name):
                os.remove(gif_name)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)