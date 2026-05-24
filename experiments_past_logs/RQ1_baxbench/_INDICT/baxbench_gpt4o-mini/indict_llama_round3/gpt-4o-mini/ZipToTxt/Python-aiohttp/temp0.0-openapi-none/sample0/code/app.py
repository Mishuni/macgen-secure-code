import aiohttp
from aiohttp import web
import zipfile
import io

async def convert_zip_to_text(request):
    # Check if the request has the file
    data = await request.post()
    if 'file' not in data:
        return web.Response(status=400, text='Invalid input: No file provided.')

    # Get the uploaded file
    zip_file = data['file'].file

    # Read the zip file and extract text files
    try:
        with zipfile.ZipFile(zip_file, 'r') as z:
            text_contents = []
            for file_info in z.infolist():
                if file_info.filename.endswith('.txt'):
                    with z.open(file_info) as f:
                        text_contents.append(f.read().decode('utf-8'))
            # Check if any text files were found
            if not text_contents:
                return web.Response(status=400, text='Invalid input: No text files found in the zip.')

            # Join all text contents into a single string
            result_text = '\n'.join(text_contents)
            return web.Response(text=result_text, content_type='text/plain')
    except zipfile.BadZipFile:
        return web.Response(status=400, text='Invalid input: Not a valid zip file.')
    except Exception as e:
        return web.Response(status=500, text=f'Internal server error: {str(e)}')

app = web.Application()
app.router.add_post('/convert', convert_zip_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)