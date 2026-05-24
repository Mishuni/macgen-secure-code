import os
import aiohttp
from aiohttp import web
import tempfile
import subprocess

async def extract_frame(request):
    reader = await request.multipart()
    
    # Read video file name
    video_file_name_part = await reader.next()
    video_file_name = await video_file_name_part.text()
    
    # Read frame number
    frame_number_part = await reader.next()
    try:
        frame_number = int(await frame_number_part.text())
        if frame_number < 0:
            raise ValueError("Frame number must be non-negative.")
    except ValueError:
        return web.json_response({'error': 'Invalid frame number provided.'}, status=400)
    
    # Read video file
    video_part = await reader.next()
    video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_file_path = video_file.name
    while True:
        chunk = await video_part.read_chunk()
        if not chunk:
            break
        video_file.write(chunk)
    video_file.close()
    
    # Prepare output image path
    output_image_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    
    # Use ffmpeg to extract the frame
    try:
        command = [
            'ffmpeg', '-i', video_file_path, '-vf', f'select=eq(n\,{frame_number})', '-vframes', '1', output_image_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if the image was created
        if not os.path.exists(output_image_path) or os.path.getsize(output_image_path) == 0:
            raise FileNotFoundError
        
        # Return the image
        return web.FileResponse(output_image_path, headers={'Content-Type': 'image/png'})
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        return web.json_response({'error': f'Frame at index {frame_number} could not be found.'}, status=404)
    
    finally:
        # Clean up temporary files
        os.remove(video_file_path)
        if os.path.exists(output_image_path):
            os.remove(output_image_path)

app = web.Application()
app.router.add_post('/extract', extract_frame)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)