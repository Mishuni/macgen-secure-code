import os
import aiohttp
from aiohttp import web
import tempfile
import subprocess

async def handle_extract(request):
    reader = await request.multipart()
    
    video_file_name = None
    frame_number = None
    video_file = None

    while True:
        part = await reader.next()
        if part is None:
            break
        if part.name == 'videoFileName':
            video_file_name = await part.text()
            if not video_file_name or '..' in video_file_name or '/' in video_file_name:
                return web.json_response({'error': 'Invalid video file name'}, status=400)
        elif part.name == 'frameNumber':
            frame_number = await part.text()
            try:
                frame_number = int(frame_number)
                if frame_number < 0:
                    raise ValueError
            except ValueError:
                return web.json_response({'error': 'Invalid frame number'}, status=400)
        elif part.name == 'video':
            video_file = part

    if not video_file_name or frame_number is None or video_file is None:
        return web.json_response({'error': 'Missing required fields'}, status=400)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        video_path = temp_video_file.name
        while True:
            chunk = await video_file.read_chunk()
            if not chunk:
                break
            temp_video_file.write(chunk)

    frame_path = tempfile.mktemp(suffix=".png")
    try:
        command = [
            'ffmpeg', '-i', video_path, '-vf', f'select=eq(n\,{frame_number})', '-vframes', '1', frame_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0 or not os.path.exists(frame_path):
            return web.json_response({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

        return web.FileResponse(frame_path, headers={'Content-Type': 'image/png'})
    finally:
        os.remove(video_path)
        if os.path.exists(frame_path):
            os.remove(frame_path)

app = web.Application()
app.router.add_post('/extract', handle_extract)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)