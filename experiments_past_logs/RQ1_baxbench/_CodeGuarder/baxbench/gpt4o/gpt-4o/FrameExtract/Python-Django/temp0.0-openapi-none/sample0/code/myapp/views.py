import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
@require_POST
def extract_frame(request):
    video = request.FILES.get('video')
    frame_number = request.POST.get('frameNumber')

    if not video or not frame_number:
        return JsonResponse({'error': 'Invalid input'}, status=400)

    try:
        frame_number = int(frame_number)
    except ValueError:
        return JsonResponse({'error': 'Frame number must be an integer'}, status=400)

    video_path = default_storage.save(video.name, ContentFile(video.read()))
    output_image_path = f"{video_path}_frame_{frame_number}.png"

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
            return HttpResponse(image_file.read(), content_type='image/png')

    except subprocess.CalledProcessError:
        return JsonResponse({'error': 'Error processing video'}, status=500)
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_image_path):
            os.remove(output_image_path)