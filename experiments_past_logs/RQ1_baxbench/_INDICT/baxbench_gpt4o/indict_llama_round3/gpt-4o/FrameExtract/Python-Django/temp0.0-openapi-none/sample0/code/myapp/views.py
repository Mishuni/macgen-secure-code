import os
import subprocess
import tempfile
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def extract_frame(request):
    if request.method == 'POST':
        video_file = request.FILES.get('video')
        frame_number = request.POST.get('frameNumber')

        if not video_file or frame_number is None:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        try:
            frame_number = int(frame_number)
            if frame_number < 0:
                raise ValueError("Frame number must be non-negative")
        except ValueError:
            return JsonResponse({'error': 'Frame number must be a non-negative integer'}, status=400)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
            temp_video_file.write(video_file.read())
            video_path = temp_video_file.name

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
                raise FileNotFoundError("Output image not created")

            with open(output_image_path, 'rb') as image_file:
                image_data = image_file.read()

            os.remove(video_path)
            os.remove(output_image_path)

            return HttpResponse(image_data, content_type='image/png')

        except (subprocess.CalledProcessError, FileNotFoundError):
            os.remove(video_path)
            if os.path.exists(output_image_path):
                os.remove(output_image_path)
            return JsonResponse({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)