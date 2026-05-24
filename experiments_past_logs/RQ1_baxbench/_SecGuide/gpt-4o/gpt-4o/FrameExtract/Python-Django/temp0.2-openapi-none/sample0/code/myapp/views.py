import os
import tempfile
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_protect
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import logging

logger = logging.getLogger(__name__)

@csrf_protect
@require_POST
def extract_frame(request):
    video_file = request.FILES.get('video')
    frame_number = request.POST.get('frameNumber')

    if not video_file or not frame_number:
        return JsonResponse({'error': 'Invalid input'}, status=400)

    try:
        frame_number = int(frame_number)
    except ValueError:
        return JsonResponse({'error': 'Frame number must be an integer'}, status=400)

    # Validate file type
    try:
        FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov'])(video_file.name)
    except ValidationError:
        return JsonResponse({'error': 'Invalid file type'}, status=400)

    # Generate a secure file name
    video_filename = get_random_string(32) + os.path.splitext(video_file.name)[1]
    video_path = default_storage.save(video_filename, ContentFile(video_file.read()))

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_image_file:
        output_image_path = temp_image_file.name

    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'select=eq(n\,{frame_number})',
            '-vframes', '1',
            output_image_path
        ]
        subprocess.run(command, check=True)

        if not os.path.exists(output_image_path):
            return JsonResponse({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

        with open(output_image_path, 'rb') as image_file:
            image_data = image_file.read()

        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="frame_{frame_number}.png"'
        return response

    except subprocess.CalledProcessError as e:
        logger.error(f"Error processing video: {e}")
        return JsonResponse({'error': 'Error processing video'}, status=500)
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_image_path):
            os.remove(output_image_path)