import asyncio
import os
import subprocess
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_exceptions import HTTPBadRequest, HTTPInternalServerError
from multidict import MultiDict
import tempfile

async def handle_create_gif(request: Request) -> Response:
    try:
        # Validate and parse input
        reader = await request.multipart()
        data = await parse_multipart_data(reader)

        # Process images and create GIF
        gif_path = await create_gif(data)

        # Return the created GIF
        return await return_gif(gif_path)

    except ValueError as e:
        return web.json_response({'error': str(e)}, status=400)
    except Exception as e:
        return web.json_response({'error': 'Internal Server Error'}, status=500)

async def parse_multipart_data(reader) -> dict:
    data = {}
    images = []

    while True:
        part = await reader.next()
        if part is None:
            break

        if part.name == 'images':
            images.append(await part.read(decode=True))
        elif part.name == 'targetSize':
            data['targetSize'] = await part.text()
        elif part.name == 'delay':
            data['delay'] = int(await part.text())
        elif part.name == 'appendReverted':
            data['appendReverted'] = await part.text().lower() == 'true'

    if not images:
        raise ValueError("No images provided")
    if 'targetSize' not in data:
        raise ValueError("Target size not provided")

    data['images'] = images
    return data

async def create_gif(data: dict) -> str:
    with tempfile.TemporaryDirectory() as tmpdirname:
        image_paths = []
        for i, image in enumerate(data['images']):
            image_path = os.path.join(tmpdirname, f'image_{i}.png')
            with open(image_path, 'wb') as f:
                f.write(image)
            image_paths.append(image_path)

        if data.get('appendReverted', False):
            image_paths.extend(reversed(image_paths))

        gif_path = os.path.join(tmpdirname, 'output.gif')
        command = [
            'convert',
            '-delay', str(data.get('delay', 10)),
            '-resize', data['targetSize'],
            *image_paths,
            gif_path
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"ImageMagick error: {stderr.decode()}")

        return gif_path

async def return_gif(gif_path: str) -> Response:
    return web.FileResponse(gif_path, headers=MultiDict({'Content-Type': 'image/gif'}))

app = web.Application()
app.router.add_post('/create-gif', handle_create_gif)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)