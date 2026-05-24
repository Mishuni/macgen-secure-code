import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import tempfile
import os

@csrf_exempt
def compile_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_name = data.get('fileName')
            file_content = data.get('fileContent')

            if not file_name or not file_content:
                return JsonResponse({'hasError': True, 'compilerError': 'Invalid input'}, status=400)

            if not (file_name.endswith('.ts') or file_name.endswith('.cpp')):
                return JsonResponse({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
                temp_file.write(file_content.encode('utf-8'))
                temp_file_path = temp_file.name

            if file_name.endswith('.ts'):
                compile_command = ['tsc', '--noEmit', '--skipLibCheck', temp_file_path]
            elif file_name.endswith('.cpp'):
                compile_command = ['g++', '-fsyntax-only', temp_file_path]

            result = subprocess.run(compile_command, capture_output=True, text=True, shell=False)
            os.remove(temp_file_path)

            if result.returncode != 0:
                return JsonResponse({'hasError': True, 'compilerError': result.stderr})

            return JsonResponse({'hasError': False, 'compilerError': None})

        except json.JSONDecodeError:
            return JsonResponse({'hasError': True, 'compilerError': 'Invalid JSON'}, status=400)

    return JsonResponse({'hasError': True, 'compilerError': 'Invalid request method'}, status=405)