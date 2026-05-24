import subprocess
import json
import os
from django.http import JsonResponse
from django.views import View

class CompileView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            file_name = data.get('fileName')
            file_content = data.get('fileContent')

            # Validate input
            if not file_name or not file_content:
                return JsonResponse({'hasError': True, 'compilerError': 'File name and content cannot be empty.'}, status=400)

            # Validate file name
            if not (file_name.endswith('.ts') or file_name.endswith('.cpp')):
                return JsonResponse({'hasError': True, 'compilerError': 'Unsupported file type.'}, status=400)

            # Save the file temporarily
            with open(file_name, 'w') as f:
                f.write(file_content)

            # Determine the file type and compile accordingly
            if file_name.endswith('.ts'):
                compile_command = ['tsc', file_name]
            elif file_name.endswith('.cpp'):
                compile_command = ['g++', file_name, '-o', 'output']

            # Run the compile command
            result = subprocess.run(compile_command, capture_output=True, text=True)

            # Check for errors
            if result.returncode != 0:
                return JsonResponse({'hasError': True, 'compilerError': result.stderr.strip()}, status=200)
            else:
                return JsonResponse({'hasError': False, 'compilerError': None}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'hasError': True, 'compilerError': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'hasError': True, 'compilerError': str(e)}, status=500)
        finally:
            # Clean up the temporary file
            if os.path.exists(file_name):
                os.remove(file_name)