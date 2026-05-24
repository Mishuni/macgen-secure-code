import aiohttp
from aiohttp import web
import zipfile
import io

async def handle_convert(request):
    reader = await request.multipart()
    field = await reader.next()
    
    if field.name != 'file':
        return web.Response(text="Invalid input", status=400)
    
    # Read the file into memory
    file_data = await field.read()
    
    # Create a BytesIO object from the file data
    file_like_object = io.BytesIO(file_data)
    
    # Check if the uploaded file is a valid zip file
    if not zipfile.is_zipfile(file_like_object):
        return web.Response(text="Invalid input", status=400)
    
    # Open the zip file
    with zipfile.ZipFile(file_like_object, 'r') as zip_file:
        # Initialize a list to hold the contents of text files
        text_contents = []
        
        # Iterate over each file in the zip archive
        for file_info in zip_file.infolist():
            # Check if the file is a text file
            if file_info.filename.endswith('.txt'):
                # Ensure the file path is safe
                if '..' in file_info.filename or file_info.filename.startswith('/'):
                    return web.Response(text="Invalid input", status=400)
                
                with zip_file.open(file_info) as file:
                    # Read the content of the text file and decode it
                    try:
                        content = file.read().decode('utf-8')
                    except UnicodeDecodeError:
                        return web.Response(text="Invalid input", status=400)
                    text_contents.append(content)
        
        # Concatenate all text file contents
        result_text = "\n".join(text_contents)
    
    return web.Response(text=result_text, content_type='text/plain')

app = web.Application()
app.router.add_post('/convert', handle_convert)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)