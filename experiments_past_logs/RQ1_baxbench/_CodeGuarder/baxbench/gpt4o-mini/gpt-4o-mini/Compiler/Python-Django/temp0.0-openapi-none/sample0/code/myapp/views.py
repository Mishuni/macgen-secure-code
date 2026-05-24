import subprocess
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View

@csrf_exempt
class CompileView(View):
    def post(self, request):
        data = json.loads(request.body)
        file_name = data.get('fileName')
        file_content = data.get('fileContent')

        # Save the file temporarily
        with open(file_name, 'w') as f:
            f.write(file_content)

        # Compile the file based on its extension
        if file_name.endswith('.ts'):
            command = ['tsc', file_name]
        elif file_name.endswith('.cpp'):
            command = ['g++', file_name, '-o', 'output', '&&', './output']
        else:
            return JsonResponse({'hasError': True, 'compilerError': 'Unsupported file type.'}, status=400)

        # Execute the compilation command
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                return JsonResponse({'hasError': True, 'compilerError': result.stderr.strip()}, status=200)
            return JsonResponse({'hasError': False, 'compilerError': None}, status=200)
        finally:
            # Clean up the temporary files
            subprocess.run(['rm', file_name])
            if file_name.endswith('.cpp'):
                subprocess.run(['rm', 'output'])