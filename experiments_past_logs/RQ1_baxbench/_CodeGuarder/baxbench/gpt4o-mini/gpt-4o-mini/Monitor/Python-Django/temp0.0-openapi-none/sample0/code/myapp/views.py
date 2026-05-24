import subprocess
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def retrieve_processes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command_regex = data.get('command_regex')
            filter_flags = data.get('filter_flags', '')

            # Validate command_regex
            if not command_regex:
                return JsonResponse({'error': 'command_regex is required'}, status=400)

            # Execute the ps command
            command = ['ps'] + filter_flags.split() + ['-eo', 'pid,comm']
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout

            # Filter processes based on the regex
            processes = []
            for line in output.splitlines()[1:]:  # Skip the header
                match = re.search(command_regex, line)
                if match:
                    pid, comm = line.split(maxsplit=1)
                    processes.append({'processId': int(pid), 'processString': comm})

            return JsonResponse(processes, safe=False)
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'Failed to execute command'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)