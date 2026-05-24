import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

@csrf_exempt
def compile_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_name = data.get('fileName')
            file_content = data.get('fileContent')

            if not file_name or not file_content:
                return JsonResponse({'error': 'Invalid input'}, status=400)

            # Determine the compiler based on file extension
            if file_name.endswith('.cpp'):
                compiler = 'g++'
                output_file = 'a.out'
            elif file_name.endswith('.ts'):
                compiler = 'tsc'
                output_file = None
            else:
                return JsonResponse({'error': 'Unsupported file type'}, status=400)

            # Write the file content to a temporary file
            temp_file_path = f'/tmp/{file_name}'
            with open(temp_file_path, 'w') as temp_file:
                temp_file.write(file_content)

            # Compile the file
            compile_command = [compiler, temp_file_path]
            if output_file:
                compile_command.extend(['-o', f'/tmp/{output_file}'])

            result = subprocess.run(
                compile_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Clean up the temporary file
            os.remove(temp_file_path)
            if output_file and os.path.exists(f'/tmp/{output_file}'):
                os.remove(f'/tmp/{output_file}')

            # Return the result
            if result.returncode == 0:
                return JsonResponse({'hasError': False, 'compilerError': None})
            else:
                return JsonResponse({'hasError': True, 'compilerError': result.stderr})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)