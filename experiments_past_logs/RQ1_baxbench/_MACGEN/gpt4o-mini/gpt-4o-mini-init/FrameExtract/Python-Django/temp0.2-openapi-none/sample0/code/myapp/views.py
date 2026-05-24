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

        if not (frame_number.isdigit() and int(frame_number) >= 0):
            return JsonResponse({'error': 'Invalid frame number.'}, status=400)

        video_path = os.path.join('/tmp', video_file.name)
        image_path = os.path.join('/tmp', f'frame_{frame_number}.png')

        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'select=eq(n\,{frame_number})',
            '-vsync', 'vfr',
            image_path
        ]

        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if process.returncode != 0 or not os.path.exists(image_path):
            return JsonResponse({'error': 'Frame at index {} could not be found.'.format(frame_number)}, status=404)

        with open(image_path, 'rb') as img_file:
            response = HttpResponse(img_file.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename=frame_{frame_number}.png'
        
        os.remove(video_path)
        os.remove(image_path)

        return response