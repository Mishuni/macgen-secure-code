import json
import subprocess
import tempfile
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def compile_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        file_name = data.get('fileName')
        file_content = data.get('fileContent')

        if not file_name or not file_content:
            return JsonResponse({'hasError': True, 'compilerError': 'Invalid input'}, status=400)

        file_extension = file_name.split('.')[-1]
        if not re.match(r'^[\w\-\.]+$', file_name) or file_extension not in ['ts', 'cpp']:
            return JsonResponse({'hasError': True, 'compilerError': 'Invalid file name or type'}, status=400)

        with tempfile.NamedTemporaryFile(delete=True, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(file_content.encode())
            temp_file.flush()

            if file_extension == 'ts':
                command = ['tsc', temp_file.name]
            elif file_extension == 'cpp':
                command = ['g++', temp_file.name, '-o', temp_file.name[:-4]]
            else:
                return JsonResponse({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode != 0:
                return JsonResponse({'hasError': True, 'compilerError': process.stderr.strip()})
            return JsonResponse({'hasError': False, 'compilerError': None})
    return JsonResponse({'hasError': True, 'compilerError': 'Method not allowed'}, status=405)