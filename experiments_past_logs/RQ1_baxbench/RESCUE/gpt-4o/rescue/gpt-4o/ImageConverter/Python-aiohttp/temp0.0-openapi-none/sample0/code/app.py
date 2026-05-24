import aiohttp
from aiohttp import web
import tempfile
import os
import subprocess
import shutil

# Helper function to parse target size
def parse_target_size(size_str):
    try:
        width, height = map(int, size_str.lower().split('x'))
        return width, height
    except ValueError:
        raise web.HTTPBadRequest(reason="Invalid targetSize format. Expected format: WIDTHxHEIGHT (e.g., 500x500).")

# Helper function to safely create a temporary directory
def create_temp_dir():
    return tempfile.mkdtemp()

# Helper function to safely clean up temporary files and directories
def cleanup_temp_dir(temp_dir):
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# Route handler for creating GIF
async def create_gif(request):
    # Ensure the request is multipart/form-data
    if not request.content_type.startswith('multipart/form-data'):
        raise web.HTTPBadRequest(reason="Content-Type must be multipart/form-data.")

    # Parse the multipart form data
    reader = await request.multipart()
    images = []
    target_size = None
    delay = 10  # Default delay
    append_reverted = False

    # Process each part of the form
    async for part in reader:
        if part.name == 'images':
            # Save each image to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            try:
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    temp_file.write(chunk)
                temp_file.close()
                images.append(temp_file.name)
            except Exception:
                temp_file.close()
                os.unlink(temp_file.name)
                raise web.HTTPInternalServerError(reason="Failed to process uploaded images.")
        elif part.name == 'targetSize':
            target_size = await part.text()
        elif part.name == 'delay':
            try:
                delay = int(await part.text())
            except ValueError:
                raise web.HTTPBadRequest(reason="Invalid delay value. Must be an integer.")
        elif part.name == 'appendReverted':
            append_reverted = (await part.text()).lower() == 'true'

    # Validate required fields
    if not images:
        raise web.HTTPBadRequest(reason="At least one image must be provided.")
    if not target_size:
        raise web.HTTPBadRequest(reason="targetSize is required.")

    # Parse and validate target size
    try:
        width, height = parse_target_size(target_size)
    except web.HTTPBadRequest as e:
        raise e

    # Create a temporary directory for processing
    temp_dir = create_temp_dir()
    try:
        # Prepare the list of input files for ImageMagick
        input_files = images[:]
        if append_reverted:
            input_files += reversed(images)

        # Generate the output GIF file path
        output_gif_path = os.path.join(temp_dir, "output.gif")

        # Build the ImageMagick command
        command = [
            "convert",
            "-delay", str(delay // 10),  # Convert milliseconds to ImageMagick delay units
            "-resize", f"{width}x{height}!",
        ] + input_files + [output_gif_path]

        # Execute the ImageMagick command
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode != 0:
            raise web.HTTPInternalServerError(reason=f"ImageMagick error: {process.stderr.decode()}")

        # Read the generated GIF file
        with open(output_gif_path, "rb") as gif_file:
            gif_data = gif_file.read()

        # Return the GIF as a response
        return web.Response(body=gif_data, content_type="image/gif")

    finally:
        # Clean up temporary files and directories
        for image in images:
            if os.path.exists(image):
                os.unlink(image)
        cleanup_temp_dir(temp_dir)

# Create the aiohttp web application
app = web.Application()
app.router.add_post('/create-gif', create_gif)

# Start the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)