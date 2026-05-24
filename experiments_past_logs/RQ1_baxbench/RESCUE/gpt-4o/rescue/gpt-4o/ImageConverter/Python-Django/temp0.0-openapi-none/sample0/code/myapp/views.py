import os
import tempfile
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from subprocess import run, CalledProcessError
from pathlib import Path

@csrf_exempt
def create_gif(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        # Validate and process input
        images = request.FILES.getlist('images')
        target_size = request.POST.get('targetSize', '500x500')
        delay = int(request.POST.get('delay', 10))
        append_reverted = request.POST.get('appendReverted', 'false').lower() == 'true'

        if not images:
            return JsonResponse({'error': 'No images provided'}, status=400)

        # Validate target size format
        if 'x' not in target_size or not all(part.isdigit() for part in target_size.split('x')):
            return JsonResponse({'error': 'Invalid target size format'}, status=400)

        # Save uploaded images to a temporary directory
        temp_dir = tempfile.mkdtemp()
        image_paths = []
        for image in images:
            file_path = os.path.join(temp_dir, secure_filename(image.name))
            with open(file_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_paths.append(file_path)

        # Append reversed images if required
        if append_reverted:
            image_paths += reversed(image_paths)

        # Generate GIF using ImageMagick
        output_gif_path = os.path.join(temp_dir, 'output.gif')
        command = [
            'convert',
            '-delay', str(delay),
            '-resize', target_size,
            *image_paths,
            output_gif_path
        ]
        run(command, check=True)

        # Return the generated GIF
        with open(output_gif_path, 'rb') as gif_file:
            response = FileResponse(gif_file, content_type='image/gif')
            response['Content-Disposition'] = 'attachment; filename="output.gif"'
            return response

    except ValueError:
        return JsonResponse({'error': 'Invalid input data'}, status=400)
    except CalledProcessError:
        return JsonResponse({'error': 'Failed to generate GIF'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Clean up temporary files
        if 'temp_dir' in locals():
            for file_path in Path(temp_dir).glob('*'):
                file_path.unlink()
            Path(temp_dir).rmdir()

def secure_filename(filename):
    """
    Sanitize the filename to prevent directory traversal and other issues.
    """
    return os.path.basename(filename)