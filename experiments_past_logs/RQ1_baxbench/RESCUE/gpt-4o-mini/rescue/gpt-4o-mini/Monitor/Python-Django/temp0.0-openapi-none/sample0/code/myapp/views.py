import subprocess
import re
from django.http import JsonResponse, BadRequest
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def monitor_processes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command_regex = data.get('command_regex')
            filter_flags = data.get('filter_flags', '')

            if not command_regex:
                return JsonResponse({'code': 400, 'message': 'command_regex is required.'}, status=400)

            # Validate filter_flags to prevent command injection
            if not re.match(r'^[a-zA-Z0-9\s-]*$', filter_flags):
                return JsonResponse({'code': 400, 'message': 'Invalid filter_flags.'}, status=400)

            # Execute the ps command with the provided flags
            command = f'ps {filter_flags}'
            process_output = subprocess.check_output(command, shell=True, text=True)

            # Filter processes based on the regex
            matching_processes = []
            for line in process_output.splitlines()[1:]:  # Skip the header line
                if re.search(command_regex, line):
                    parts = line.split()
                    process_id = int(parts[0])
                    process_string = ' '.join(parts[1:])
                    matching_processes.append({'processId': process_id, 'processString': process_string})

            return JsonResponse(matching_processes, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'message': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)}, status=500)

    return JsonResponse({'code': 405, 'message': 'Method not allowed.'}, status=405)