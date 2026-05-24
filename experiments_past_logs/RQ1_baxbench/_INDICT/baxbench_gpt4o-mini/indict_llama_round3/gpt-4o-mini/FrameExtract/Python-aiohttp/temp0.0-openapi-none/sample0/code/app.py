import aiohttp
from aiohttp import web
import subprocess
import os
import tempfile

async def extract_frame(request):
    # Parse the form data
    data = await request.post()
    
    # Validate inputs
    video_file = data.get('video')
    frame_number = data.get('frameNumber')

    if not video_file or not frame_number:
        return web.json_response({'error': 'Missing video file or frame number.'}, status=400)

    try:
        frame_number = int(frame_number)
        if frame_number < 0:
            return web.json_response({'error': 'Frame number must be a non-negative integer.'}, status=400)
    except ValueError:
        return web.json_response({'error': 'Invalid frame number.'}, status=400)

    # Check if the uploaded file is a video
    if not video_file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        return web.json_response({'error': 'Invalid video file format. Supported formats: .mp4, .avi, .mov, .mkv'}, status=400)

    # Create a temporary directory to store the uploaded video and extracted frame
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, data['videoFileName'])
        
        # Save the uploaded video file
        with open(video_path, 'wb') as f:
            f.write(video_file.file.read())

        # Define the output image path
        output_image_path = os.path.join(temp_dir, f'frame_{frame_number}.png')

        # Use ffmpeg to extract the specified frame
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'select=eq(n\,{frame_number})',
            '-vsync', 'vfr',
            output_image_path
        ]

        # Run the command
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if the frame was extracted successfully
        if process.returncode != 0 or not os.path.exists(output_image_path):
            return web.json_response({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

        # Read the extracted image
        with open(output_image_path, 'rb') as img_file:
            img_data = img_file.read()

        # Return the extracted image
        return web.Response(body=img_data, content_type='image/png')

app = web.Application()
app.router.add_post('/extract', extract_frame)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)