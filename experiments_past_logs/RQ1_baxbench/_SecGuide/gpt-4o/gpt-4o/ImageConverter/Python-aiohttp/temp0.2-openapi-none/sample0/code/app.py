import aiohttp
from aiohttp import web
import asyncio
import os
import tempfile
from PIL import Image

async def handle_create_gif(request):
    try:
        reader = await request.multipart()
        images = []
        target_size = None
        delay = 10
        append_reverted = False

        # Create a secure temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            while True:
                part = await reader.next()
                if part is None:
                    break

                if part.name == 'images':
                    # Validate image content type
                    if part.headers.get('Content-Type') not in ['image/png', 'image/jpeg']:
                        return web.json_response({'error': 'Invalid image format'}, status=400)

                    # Save the image to a temporary file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png", dir=temp_dir)
                    images.append(temp_file.name)
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        temp_file.write(chunk)
                    temp_file.close()

                elif part.name == 'targetSize':
                    target_size = await part.text()
                    if not target_size.isdigit() or int(target_size) <= 0:
                        return web.json_response({'error': 'Invalid target size'}, status=400)

                elif part.name == 'delay':
                    delay_text = await part.text()
                    if delay_text.isdigit() and int(delay_text) > 0:
                        delay = int(delay_text)
                    else:
                        return web.json_response({'error': 'Invalid delay'}, status=400)

                elif part.name == 'appendReverted':
                    append_reverted = (await part.text()).lower() == 'true'

            if not images or not target_size:
                return web.json_response({'error': 'Missing required fields'}, status=400)

            # Validate and process images
            processed_images = []
            for image_path in images:
                with Image.open(image_path) as img:
                    img = img.resize((int(target_size), int(target_size)))
                    processed_images.append(img.copy())

            if append_reverted:
                processed_images.extend(reversed(processed_images))

            # Create GIF
            output_gif = tempfile.NamedTemporaryFile(delete=False, suffix=".gif", dir=temp_dir).name
            processed_images[0].save(output_gif, save_all=True, append_images=processed_images[1:], duration=delay, loop=0)

            # Read the generated GIF
            with open(output_gif, 'rb') as f:
                gif_data = f.read()

            return web.Response(body=gif_data, content_type='image/gif')

    except Exception as e:
        # Log the exception securely
        print(f"Error: {e}")
        return web.json_response({'error': 'An internal server error occurred'}, status=500)

app = web.Application()
app.router.add_post('/create-gif', handle_create_gif)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)