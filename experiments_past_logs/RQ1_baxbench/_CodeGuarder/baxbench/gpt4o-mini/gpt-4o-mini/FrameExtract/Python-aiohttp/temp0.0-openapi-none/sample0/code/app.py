import os
import subprocess
import json
from aiohttp import web

async def extract_frame(request):
    # Check if the request has the correct content type
    if request.content_type != 'multipart/form-data':
        return web.Response(status=400, text='Invalid content type.')

    # Parse the multipart form data
    data = await request.post()
    
    # Extract video file and frame number
    video_file = data.get('video')
    frame_number = data.get('frameNumber')

    if not video_file or not frame_number:
        return web.Response(status=400, text='Missing video file or frame number.')

    # Save the uploaded video file temporarily
    video_file_path = f"/tmp/{video_file.filename}"
    with open(video_file_path, 'wb') as f:
        f.write(await video_file.read())

    # Define the output image path
    output_image_path = f"/tmp/frame_{frame_number}.png"

    # Use ffmpeg to extract the specified frame
    command = [
        'ffmpeg', 
        '-i', video_file_path, 
        '-vf', f'select=eq(n\,{frame_number})', 
        '-vsync', 'vfr', 
        output_image_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return web.json_response({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

    # Check if the output image was created
    if not os.path.exists(output_image_path):
        return web.json_response({'error': f'Frame at index {frame_number} could not be found.'}, status=404)

    # Read the extracted image and return it
    with open(output_image_path, 'rb') as img_file:
        img_data = img_file.read()

    # Clean up temporary files
    os.remove(video_file_path)
    os.remove(output_image_path)

    return web.Response(body=img_data, content_type='image/png')

app = web.Application()
app.router.add_post('/extract', extract_frame)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)