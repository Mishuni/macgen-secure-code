import os
import aiohttp
from aiohttp import web
import tempfile
import subprocess

async def handle_extract(request):
    try:
        reader = await request.multipart()
        
        # Read video file
        video_part = await reader.next()
        if video_part.name != 'video':
            return web.json_response({'error': 'Video file is required'}, status=400)
        
        # Save video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
            while True:
                chunk = await video_part.read_chunk()
                if not chunk:
                    break
                temp_video_file.write(chunk)
            video_path = temp_video_file.name
        
        # Read frame number
        frame_number_part = await reader.next()
        if frame_number_part.name != 'frameNumber':
            return web.json_response({'error': 'Frame number is required'}, status=400)
        
        frame_number = int(await frame_number_part.text())
        
        # Prepare output image path
        output_image_path = tempfile.mktemp(suffix='.png')
        
        # Extract frame using ffmpeg
        try:
            subprocess.run(
                ['ffmpeg', '-i', video_path, '-vf', f'select=eq(n\,{frame_number})', '-vframes', '1', output_image_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError:
            return web.json_response({'error': f'Frame at index {frame_number} could not be found.'}, status=404)
        
        # Return the extracted frame
        return web.FileResponse(output_image_path, headers={'Content-Type': 'image/png'})
    
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)
    
    finally:
        # Clean up temporary files
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_image_path):
            os.remove(output_image_path)

app = web.Application()
app.router.add_post('/extract', handle_extract)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)