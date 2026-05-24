import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def extract_frame(request):
    if request.method == 'POST':
        video_file = request.FILES.get('video')
        frame_number = request.POST.get('frameNumber')

        if not video_file or not frame_number:
            return JsonResponse({'error': 'Missing video file or frame number.'}, status=400)

        try:
            frame_number = int(frame_number)
            if frame_number < 0:
                return JsonResponse({'error': 'Frame number must be a non-negative integer.'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Frame number must be an integer.'}, status=400)

        video_path = f'/tmp/{video_file.name}'
        output_image_path = f'/tmp/frame_{frame_number}.png'

        # Save the uploaded video file
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        # Use ffmpeg to extract the frame
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'select=eq(n\,{frame_number})',
            '-vframes', '1',
            output_image_path
        ]

        try:
            subprocess.run(command, check=True)
            if os.path.exists(output_image_path):
                with open(output_image_path, 'rb') as img_file:
                    response = HttpResponse(img_file.read(), content_type='image/png')
                    response['Content-Disposition'] = f'attachment; filename="frame_{frame_number}.png"'
                return response
            else:
                return JsonResponse({'error': f'Frame at index {frame_number} could not be found.'}, status=404)
        except subprocess.CalledProcessError:
            return JsonResponse({'error': f'Frame at index {frame_number} could not be found.'}, status=404)
        finally:
            # Clean up temporary files
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(output_image_path):
                os.remove(output_image_path)