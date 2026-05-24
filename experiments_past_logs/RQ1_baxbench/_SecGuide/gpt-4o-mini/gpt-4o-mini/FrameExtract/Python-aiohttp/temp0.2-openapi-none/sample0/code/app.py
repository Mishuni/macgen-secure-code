import aiohttp
from aiohttp import web
import subprocess
import os
import tempfile
import shlex

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}  # Define allowed video file extensions
MAX_FRAME_NUMBER = 10000  # Define a maximum frame number limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # Define a maximum file size limit (10 MB)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def extract_frame(request):
    # Check if the request has the correct content type
    if not request.has_body:
        return web.json_response({"error": "No file uploaded."}, status=400)

    # Parse the form data
    data = await request.post()
    video_file = data.get('video')
    frame_number = data.get('frameNumber')

    if not video_file or not frame_number:
        return web.json_response({"error": "Missing video file or frame number."}, status=400)

    # Validate frame number
    try:
        frame_number = int(frame_number)
        if frame_number < 0 or frame_number > MAX_FRAME_NUMBER:
            return web.json_response({"error": f"Frame number must be between 0 and {MAX_FRAME_NUMBER}."}, status=400)
    except ValueError:
        return web.json_response({"error": "Frame number must be an integer."}, status=400)

    # Validate file size
    if video_file.size > MAX_FILE_SIZE:
        return web.json_response({"error": "Uploaded file is too large."}, status=400)

    # Validate file type
    if not allowed_file(video_file.filename):
        return web.json_response({"error": "Invalid file type. Only video files are allowed."}, status=400)

    # Create a temporary directory to store the uploaded video
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, os.path.basename(video_file.filename))
        
        # Save the uploaded video file
        with open(video_path, 'wb') as f:
            f.write(await video_file.read())

        # Define the output image path
        output_image_path = os.path.join(temp_dir, f'frame_{frame_number}.png')

        # Use ffmpeg to extract the specified frame
        command = [
            'ffmpeg', '-i', video_path, '-vf', f'select=eq(n\,{frame_number})', '-vsync', 'vfr', output_image_path
        ]
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            return web.json_response({"error": "Frame could not be extracted."}, status=404)

        # Stream the extracted image directly to the response
        return web.FileResponse(output_image_path, content_type='image/png')

app = web.Application()
app.router.add_post('/extract', extract_frame)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)