import subprocess
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def extract_frame(request):
    if request.method == 'POST':
        video_file = request.FILES.get('video')
        frame_number = request.POST.get('frameNumber')

        if not video_file or not frame_number:
            return JsonResponse({'error': 'Missing video file or frame number.'}, status=400)

        frame_number = int(frame_number)

        # Save the uploaded video file
        video_path = os.path.join('uploads', video_file.name)
        os.makedirs('uploads', exist_ok=True)
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        # Extract the frame using ffmpeg
        output_image_path = os.path.join('uploads', f'frame_{frame_number}.png')
        command = [
            'ffmpeg', '-i', video_path, '-vf', f'select=eq(n\,{frame_number})', '-vsync', 'vfr', output_image_path
        ]
        subprocess.run(command, check=True)

        # Check if the frame was extracted
        if not os.path.exists(output_image_path):
            return JsonResponse({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

        with open(output_image_path, 'rb') as img:
            response = HttpResponse(img.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename=frame_{frame_number}.png'
            return response
    return JsonResponse({'error': 'Invalid request method.'}, status=405)