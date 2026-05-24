import subprocess
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

@require_POST
def compile_code(request):
    try:
        data = json.loads(request.body)
        file_name = data.get('fileName')
        file_content = data.get('fileContent')

        if not file_name or not file_content:
            return JsonResponse({'hasError': True, 'compilerError': 'Invalid input'}, status=400)

        # Determine the file extension
        _, file_extension = os.path.splitext(file_name)

        # Use a secure method for creating temporary files
        with tempfile.NamedTemporaryFile(delete=True, suffix=file_extension) as temp_file:
            temp_file.write(file_content.encode('utf-8'))
            temp_file.flush()
            temp_file_name = temp_file.name

            # Compile the file based on its extension
            if file_extension == '.cpp':
                compile_command = ['g++', temp_file_name, '-o', temp_file_name + '_output']
            elif file_extension == '.ts':
                compile_command = ['tsc', temp_file_name]
            else:
                return JsonResponse({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

            # Execute the compile command
            result = subprocess.run(compile_command, capture_output=True, text=True)

            if result.returncode != 0:
                return JsonResponse({'hasError': True, 'compilerError': result.stderr})

        return JsonResponse({'hasError': False, 'compilerError': None})

    except Exception as e:
        logger.error("Error during code compilation", exc_info=True)
        return JsonResponse({'hasError': True, 'compilerError': 'An error occurred during compilation'}, status=500)