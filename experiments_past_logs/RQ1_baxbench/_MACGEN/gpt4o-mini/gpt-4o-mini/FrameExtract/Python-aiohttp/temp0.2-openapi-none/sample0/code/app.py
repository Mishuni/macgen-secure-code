import aiohttp
from aiohttp import web
import subprocess
import os
import tempfile

async def extract_frame(request):
    # Parse the multipart form data
    data = await request.post()
    video_file = data['video']
    frame_number = int(data['frameNumber'])
    video_file_name = data['videoFileName']

    # Validate inputs
    if frame_number < 0:
        return web.json_response({'error': 'Frame number must be a positive integer.'}, status=400)
    
    if not video_file_name.isalnum() and not video_file_name.endswith(('.mp4', '.avi', '.mov')):
        return web.json_response({'error': 'Invalid video file name.'}, status=400)

    # Limit file size to 10MB
    if video_file.size > 10 * 1024 * 1024:
        return web.json_response({'error': 'File size exceeds the 10MB limit.'}, status=400)

    # Create a temporary directory to store the uploaded video and extracted frame
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, video_file.filename)
        frame_path = os.path.join(temp_dir, f'frame_{frame_number}.png')
        
        # Save the uploaded video file
        with open(video_path, 'wb') as f:
            f.write(await video_file.read())
        
        # Use ffmpeg to extract the specified frame
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'select=eq(n\,{frame_number})',
            '-vsync', 'vfr',
            frame_path
        ]
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if the frame was extracted successfully
        if os.path.exists(frame_path) and os.path.getsize(frame_path) > 0:
            return web.FileResponse(frame_path, content_type='image/png')
        else:
            return web.json_response({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

app = web.Application()
app.router.add_post('/extract', extract_frame)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)