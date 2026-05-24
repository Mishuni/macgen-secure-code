import aiohttp
from aiohttp import web
import os
import tempfile
import subprocess
import re

async def handle_create_gif(request):
    try:
        reader = await request.multipart()
        
        # Read images
        images = []
        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == 'images':
                filename = part.filename
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
                with open(temp_file.name, 'wb') as f:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        f.write(chunk)
                images.append(temp_file.name)
        
        # Read targetSize
        target_size = None
        part = await reader.next()
        if part and part.name == 'targetSize':
            target_size = await part.text()
            if not re.match(r'^\d+x\d+$', target_size):
                return web.json_response({'error': 'Invalid targetSize format. Expected format: WIDTHxHEIGHT'}, status=400)
        
        # Read delay
        delay = 10  # default value
        part = await reader.next()
        if part and part.name == 'delay':
            try:
                delay = int(await part.text())
            except ValueError:
                return web.json_response({'error': 'Invalid delay value. Must be an integer.'}, status=400)
        
        # Read appendReverted
        append_reverted = False  # default value
        part = await reader.next()
        if part and part.name == 'appendReverted':
            append_reverted = (await part.text()).lower() == 'true'
        
        if not images or not target_size:
            return web.json_response({'error': 'images and targetSize are required'}, status=400)
        
        # Prepare the command for ImageMagick
        output_gif = tempfile.NamedTemporaryFile(delete=False, suffix='.gif').name
        command = ['convert']
        
        # Add images to the command
        command.extend(images)
        
        # Append reverted images if needed
        if append_reverted:
            command.extend(reversed(images))
        
        # Set delay and target size
        command.extend(['-delay', str(delay), '-resize', target_size, output_gif])
        
        # Execute the command
        subprocess.run(command, check=True)
        
        # Read the output GIF
        with open(output_gif, 'rb') as f:
            gif_data = f.read()
        
        # Clean up temporary files
        for image in images:
            os.remove(image)
        os.remove(output_gif)
        
        return web.Response(body=gif_data, content_type='image/gif')
    
    except subprocess.CalledProcessError as e:
        return web.json_response({'error': 'Failed to create GIF'}, status=500)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

app = web.Application()
app.router.add_post('/create-gif', handle_create_gif)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)