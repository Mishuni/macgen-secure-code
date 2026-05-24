from express import Express
from multer import Multer
from subprocess import run, PIPE
import os
import re
import tempfile

app = Express()
upload = Multer().array('images')

def validate_target_size(target_size):
    return re.match(r'^\d+x\d+$', target_size)

def validate_delay(delay):
    return delay.isdigit() and 1 <= int(delay) <= 1000

def validate_boolean(value):
    return str(value).lower() in ['true', 'false']

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

@app.post('/create-gif')
def create_gif(req, res):
    upload(req, res, lambda err: handle_upload(err, req, res))

def handle_upload(err, req, res):
    if err:
        return res.status(400).json({'error': 'File upload error'})

    images = req.files
    target_size = req.body.get('targetSize')
    delay = req.body.get('delay', '10')
    append_reverted = req.body.get('appendReverted', 'false')

    if not images or not target_size or not validate_target_size(target_size) or not validate_delay(delay) or not validate_boolean(append_reverted):
        return res.status(400).json({'error': 'Invalid input parameters'})

    append_reverted = append_reverted.lower() == 'true'

    try:
        image_paths = []
        for file in images:
            sanitized_filename = sanitize_filename(file.filename)
            sanitized_path = os.path.join(tempfile.gettempdir(), sanitized_filename)
            os.rename(file.path, sanitized_path)
            image_paths.append(sanitized_path)

        if append_reverted:
            image_paths += list(reversed(image_paths))

        with tempfile.NamedTemporaryFile(delete=False, suffix='.gif', dir=tempfile.gettempdir()) as temp_output:
            output_path = temp_output.name

        command = [
            'convert',
            '-delay', str(delay),
            '-resize', target_size,
            *image_paths,
            output_path
        ]

        result = run(command, stdout=PIPE, stderr=PIPE)
        if result.returncode != 0:
            raise Exception('Error creating GIF')

        with open(output_path, 'rb') as gif_file:
            gif_data = gif_file.read()

        os.remove(output_path)
        for path in image_paths:
            os.remove(path)

        res.set('Content-Type', 'image/gif')
        res.send(gif_data)

    except Exception as e:
        res.status(500).json({'error': 'Internal server error'})

app.listen(5000, '127.0.0.1', lambda: print('Server running on http://127.0.0.1:5000'))