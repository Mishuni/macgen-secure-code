import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@csrf_exempt
def extract_frame(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # Validate and sanitize inputs
    video = request.FILES.get('video')
    frame_number = request.POST.get('frameNumber')

    if not video or not frame_number:
        return JsonResponse({'error': 'Missing video or frameNumber'}, status=400)

    try:
        frame_number = int(frame_number)
        if frame_number < 0:
            raise ValueError("Frame number must be non-negative")
    except ValueError:
        return JsonResponse({'error': 'Invalid frameNumber'}, status=400)

    # Save the uploaded video securely
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    video_name = fs.save(video.name, video)
    video_path = fs.path(video_name)

    # Generate output frame path
    frame_path = os.path.join(settings.MEDIA_ROOT, f'frame_{frame_number}.png')

    try:
        # Use ffmpeg to extract the frame
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'select=eq(n\\,{frame_number})',
            '-vframes', '1',
            frame_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(frame_path):
            return JsonResponse({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

        # Return the extracted frame
        with open(frame_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/png')
            response['Content-Disposition'] = f'inline; filename="frame_{frame_number}.png"'
            return response
    except subprocess.CalledProcessError:
        return JsonResponse({'error': 'Error processing video file'}, status=500)
    finally:
        # Clean up temporary files
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(frame_path):
            os.remove(frame_path)