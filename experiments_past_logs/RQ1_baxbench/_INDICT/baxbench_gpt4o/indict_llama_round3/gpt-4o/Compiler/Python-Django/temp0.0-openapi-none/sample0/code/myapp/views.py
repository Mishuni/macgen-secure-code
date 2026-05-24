import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import tempfile

@csrf_exempt
def compile_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_name = data.get('fileName')
            file_content = data.get('fileContent')

            if not file_name or not file_content:
                return JsonResponse({'hasError': True, 'compilerError': 'Invalid input'}, status=400)

            # Create a temporary directory to store the file
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, file_name)

                # Write the file content to a temporary file
                with open(file_path, 'w') as code_file:
                    code_file.write(file_content)

                # Determine the compiler based on file extension
                if file_name.endswith('.cpp'):
                    compile_command = ['g++', file_path, '-o', os.path.join(temp_dir, 'output')]
                elif file_name.endswith('.ts'):
                    compile_command = ['tsc', file_path]
                else:
                    return JsonResponse({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

                # Run the compiler
                result = subprocess.run(compile_command, capture_output=True, text=True)

                if result.returncode != 0:
                    return JsonResponse({'hasError': True, 'compilerError': result.stderr})

                return JsonResponse({'hasError': False, 'compilerError': None})

        except Exception as e:
            return JsonResponse({'hasError': True, 'compilerError': str(e)}, status=500)

    return JsonResponse({'hasError': True, 'compilerError': 'Invalid request method'}, status=405)