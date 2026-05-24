import subprocess
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
def compile_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_name = data.get('fileName')
            file_content = data.get('fileContent')

            # Validate input
            if not isinstance(file_name, str) or not isinstance(file_content, str):
                return JsonResponse({'hasError': True, 'compilerError': 'Invalid input'}, status=400)

            # Write the code to a temporary file
            with open(file_name, 'w') as code_file:
                code_file.write(file_content)

            # Compile the code using g++
            compile_command = ['g++', file_name, '-o', 'output']
            compile_process = subprocess.run(compile_command, capture_output=True, text=True)

            if compile_process.returncode != 0:
                return JsonResponse({'hasError': True, 'compilerError': compile_process.stderr.strip()})
            else:
                return JsonResponse({'hasError': False, 'compilerError': None})

        except json.JSONDecodeError:
            return JsonResponse({'hasError': True, 'compilerError': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'hasError': True, 'compilerError': str(e)}, status=500)

    return JsonResponse({'hasError': True, 'compilerError': 'Method not allowed'}, status=405)