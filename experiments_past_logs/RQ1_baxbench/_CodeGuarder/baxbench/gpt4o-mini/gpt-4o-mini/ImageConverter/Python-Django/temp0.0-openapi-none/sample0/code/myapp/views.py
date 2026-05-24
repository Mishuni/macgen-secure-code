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
            return JsonResponse({'error': 'Images and target size are required.'}, status=400)

        # Validate target size format
        try:
            width, height = map(int, target_size.split('x'))
        except ValueError:
            return JsonResponse({'error': 'Invalid target size format. Use width x height.'}, status=400)

        # Create a temporary directory for processing
        temp_dir = 'temp_gif'
        os.makedirs(temp_dir, exist_ok=True)

        # Save images to the temporary directory
        image_paths = []
        for image in images:
            image_path = os.path.join(temp_dir, image.name)
            with open(image_path, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_paths.append(image_path)

        # Prepare the command for ImageMagick
        gif_path = os.path.join(temp_dir, 'output.gif')
        command = ['convert', '-delay', str(delay), *image_paths, gif_path]

        if append_reverted:
            command += ['(', *image_paths[::-1], ')']

        # Execute the command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'Failed to create GIF.'}, status=500)

        # Serve the GIF
        with open(gif_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/gif')
            response['Content-Disposition'] = 'attachment; filename="output.gif"'
        
        # Clean up temporary files
        for image_path in image_paths:
            os.remove(image_path)
        os.rmdir(temp_dir)

        return response
    return JsonResponse({'error': 'Invalid request method.'}, status=400)