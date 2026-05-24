import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

@csrf_exempt
def extract_frame(request):
    if request.method == 'POST':
        video_file = request.FILES.get('video')
        frame_number = request.POST.get('frameNumber')

        if not video_file or not frame_number:
            return JsonResponse({'error': 'Missing video file or frame number.'}, status=400)

        # Validate frame number
        try:
            frame_number = int(frame_number)
            if frame_number < 0:
                raise ValueError("Frame number must be non-negative.")
        except ValueError:
            return JsonResponse({'error': 'Invalid frame number.'}, status=400)

        # Save the uploaded video file
        fs = FileSystemStorage()
        video_file_name = fs.save(video_file.name, video_file)
        video_file_path = fs.url(video_file_name)

        # Define output image path
        output_image_path = os.path.join('/tmp', f'frame_{frame_number}.png')

        # Use ffmpeg to extract the frame
        command = [
            'ffmpeg',
            '-i', video_file_path,
            '-vf', f'select=eq(n\,{frame_number})',
            '-vsync', 'vfr',
            output_image_path
        ]

        try:
            subprocess.run(command, check=True)
            with open(output_image_path, 'rb') as img_file:
                response = HttpResponse(img_file.read(), content_type='image/png')
                response['Content-Disposition'] = f'attachment; filename="frame_{frame_number}.png"'
            return response
        except subprocess.CalledProcessError:
            return JsonResponse({'error': f'Frame at index {frame_number} could not be found.'}, status=404)
        finally:
            # Clean up the uploaded video file and output image
            if os.path.exists(video_file_path):
                os.remove(video_file_path)
            if os.path.exists(output_image_path):
                os.remove(output_image_path)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)