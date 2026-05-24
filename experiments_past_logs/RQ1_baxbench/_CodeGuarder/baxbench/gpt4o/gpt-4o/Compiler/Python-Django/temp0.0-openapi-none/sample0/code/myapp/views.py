import subprocess
import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

@method_decorator(csrf_exempt, name='dispatch')
class CompileView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            file_name = data.get('fileName')
            file_content = data.get('fileContent')

            if not file_name or not file_content:
                return JsonResponse({'error': 'Invalid input'}, status=400)

            # Determine the file extension
            _, file_extension = os.path.splitext(file_name)

            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, file_name)

                # Write the file content to a temporary file
                with open(file_path, 'w') as temp_file:
                    temp_file.write(file_content)

                # Compile the file based on its extension
                if file_extension == '.ts':
                    result = subprocess.run(['tsc', file_path], capture_output=True, text=True)
                elif file_extension == '.cpp':
                    result = subprocess.run(['g++', file_path, '-o', os.path.join(temp_dir, 'output')], capture_output=True, text=True)
                else:
                    return JsonResponse({'error': 'Unsupported file type'}, status=400)

                # Check for compilation errors
                if result.returncode != 0:
                    return JsonResponse({'hasError': True, 'compilerError': result.stderr})

                return JsonResponse({'hasError': False, 'compilerError': None})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)