import os
import zipfile
from aiohttp import web
import aiohttp
import tempfile

async def handle_convert(request):
    reader = await request.multipart()
    field = await reader.next()
    
    if field.name != 'file':
        return web.Response(text="Invalid input", status=400)
    
    # Create a temporary directory to extract the zip file
    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_path = os.path.join(tmpdirname, 'uploaded.zip')
        
        # Write the uploaded file to a temporary location
        with open(zip_path, 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                f.write(chunk)
        
        # Validate and extract the zip file
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check for Zip Slip vulnerability
                for member in zip_ref.namelist():
                    member_path = os.path.join(tmpdirname, member)
                    if not os.path.abspath(member_path).startswith(os.path.abspath(tmpdirname)):
                        raise Exception("Zip Slip detected")
                
                zip_ref.extractall(tmpdirname)
        except zipfile.BadZipFile:
            return web.Response(text="Invalid zip file", status=400)
        except Exception as e:
            return web.Response(text=str(e), status=400)
        
        # Concatenate text files
        concatenated_text = ""
        for root, _, files in os.walk(tmpdirname):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        concatenated_text += f.read() + "\n"
        
        return web.Response(text=concatenated_text, content_type='text/plain')

app = web.Application()
app.router.add_post('/convert', handle_convert)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)