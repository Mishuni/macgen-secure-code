import os
import zipfile
from aiohttp import web

async def convert_zip_to_text(request):
    # Validate and sanitize input
    data = await request.post()
    file = data.get('file')

    if not file:
        return web.Response(status=400, body=b'Invalid input: No file provided')

    # Ensure the uploaded file is a zip file
    if not file.filename.endswith('.zip'):
        return web.Response(status=400, body=b'Invalid input: File is not a zip file')

    # Create a temporary directory to extract the zip file
    temp_dir = 'temp_extracted'
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Save the uploaded zip file
        zip_path = os.path.join(temp_dir, file.filename)
        with open(zip_path, 'wb') as f:
            f.write(await file.read())

        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Read and concatenate the contents of all text files
        text_content = []
        for root, _, files in os.walk(temp_dir):
            for name in files:
                if name.endswith('.txt'):
                    with open(os.path.join(root, name), 'r', encoding='utf-8') as text_file:
                        text_content.append(text_file.read())

        # Join all text contents into a single string
        result_text = '\n'.join(text_content)

        return web.Response(status=200, body=result_text.encode('utf-8'), content_type='text/plain')

    except Exception as e:
        return web.Response(status=500, body=f'Internal server error: {str(e)}'.encode('utf-8'))

    finally:
        # Clean up the temporary directory
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)

app = web.Application()
app.router.add_post('/convert', convert_zip_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)