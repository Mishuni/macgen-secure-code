import aiohttp
from aiohttp import web
import tempfile
import os
import subprocess

async def extract_frame(request):
    # Parse the multipart form data
    data = await request.post()
    video_file = data['video']
    frame_number = int(data['frameNumber'])

    # Create a temporary file to store the uploaded video
    fd, video_path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)  # Close the file descriptor

    # Write the uploaded video to the temporary file
    with open(video_path, 'wb') as f:
        f.write(await video_file.read())

    # Create a temporary file for the extracted frame image
    fd, frame_path = tempfile.mkstemp(suffix=".png")
    os.close(fd)  # Close the file descriptor

    # Use ffmpeg to extract the specified frame
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'select=eq(n\,{frame_number})',
        '-vsync', 'vfr',
        frame_path
    ]

    try:
        # Run the ffmpeg command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if the frame was extracted successfully
        if result.returncode != 0:
            return web.json_response({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

        # Read the extracted frame image
        with open(frame_path, 'rb') as f:
            frame_image = f.read()

        return web.Response(body=frame_image, content_type='image/png')

    finally:
        # Clean up temporary files
        os.remove(video_path)
        os.remove(frame_path)

app = web.Application()
app.router.add_post('/extract', extract_frame)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)