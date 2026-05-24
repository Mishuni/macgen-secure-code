import os
import re
import aiohttp
from aiohttp import web
import tempfile
import subprocess

async def handle_create_gif(request):
    try:
        reader = await request.multipart()
        images = []
        target_size = None
        delay = 10
        append_reverted = False

        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == 'images':
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                images.append(temp_file.name)
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    temp_file.write(chunk)
                temp_file.close()
            elif part.name == 'targetSize':
                target_size = await part.text()
                if not re.match(r'^\d+x\d+$', target_size):
                    return web.json_response({'error': 'Invalid targetSize format'}, status=400)
            elif part.name == 'delay':
                delay = int(await part.text())
                if delay < 0:
                    return web.json_response({'error': 'Delay must be a non-negative integer'}, status=400)
            elif part.name == 'appendReverted':
                append_reverted = (await part.text()).lower() == 'true'

        if not images or not target_size:
            return web.json_response({'error': 'Missing required fields'}, status=400)

        output_gif = tempfile.NamedTemporaryFile(delete=False, suffix=".gif").name
        convert_command = ['convert', '-delay', str(delay), '-resize', target_size]

        convert_command.extend(images)
        if append_reverted:
            convert_command.extend(reversed(images))
        convert_command.append(output_gif)

        subprocess.run(convert_command, check=True, shell=False)

        with open(output_gif, 'rb') as f:
            gif_data = f.read()

        for image in images:
            os.remove(image)
        os.remove(output_gif)

        return web.Response(body=gif_data, content_type='image/gif')

    except subprocess.CalledProcessError:
        return web.json_response({'error': 'Error processing images'}, status=500)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

app = web.Application()
app.router.add_post('/create-gif', handle_create_gif)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)