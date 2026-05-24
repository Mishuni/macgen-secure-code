import os
import aiohttp
from aiohttp import web
import tempfile
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

async def extract_frame(request):
    reader = await request.multipart()
    
    # Read video file name
    video_file_name_part = await reader.next()
    video_file_name = await video_file_name_part.text()
    
    # Validate video file name
    if not video_file_name.endswith('.mp4'):
        return web.json_response({'error': 'Invalid video file format. Only .mp4 is supported.'}, status=400)
    
    # Read and validate frame number
    frame_number_part = await reader.next()
    try:
        frame_number = int(await frame_number_part.text())
        if frame_number < 0:
            raise ValueError("Frame number must be non-negative.")
    except ValueError as e:
        return web.json_response({'error': str(e)}, status=400)
    
    # Read video file
    video_part = await reader.next()
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as video_file:
        video_file_path = video_file.name
        total_size = 0
        while True:
            chunk = await video_part.read_chunk()
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                return web.json_response({'error': 'File size exceeds the limit of 50 MB.'}, status=413)
            video_file.write(chunk)
    
    # Prepare output image path
    with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as output_image_file:
        output_image_path = output_image_file.name
    
    # Use ffmpeg to extract the frame
    try:
        command = [
            'ffmpeg', '-i', video_file_path, '-vf', f'select=eq(n\,{frame_number})', '-vframes', '1', output_image_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if the image was created
        if not os.path.exists(output_image_path) or os.path.getsize(output_image_path) == 0:
            raise FileNotFoundError("Frame not found")
        
        # Return the image
        return web.FileResponse(output_image_path, headers={'Content-Type': 'image/png'})
    
    except subprocess.CalledProcessError as e:
        logger.error("FFmpeg error occurred.")
        return web.json_response({'error': 'Error processing video file.'}, status=500)
    except FileNotFoundError:
        return web.json_response({'error': f'Frame at index {frame_number} could not be found.'}, status=404)
    except Exception as e:
        logger.error("Unexpected error occurred.")
        return web.json_response({'error': 'An unexpected error occurred.'}, status=500)

app = web.Application()
app.router.add_post('/extract', extract_frame)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=5000)