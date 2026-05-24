import re
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def monitor_commands(request):
    try:
        data = json.loads(request.body)
        filter_flags = data.get('filter_flags', 'aux')
        command_regex = data['command_regex']

        # Validate the command_regex to prevent potential ReDoS attacks
        try:
            re.compile(command_regex)
        except re.error:
            return JsonResponse({'error': 'Invalid regular expression'}, status=400)

        # Sanitize filter_flags to allow only safe flags
        allowed_flags = {'a', 'u', 'x', 'T'}
        if not all(flag in allowed_flags for flag in filter_flags.replace('-', '')):
            return JsonResponse({'error': 'Invalid filter flags'}, status=400)

        # Run the ps command safely
        result = subprocess.run(['ps', filter_flags], capture_output=True, text=True, check=True)
        processes = result.stdout.splitlines()

        # Filter processes based on the command regex
        matching_processes = []
        for process in processes[1:]:  # Skip the header line
            if re.search(command_regex, process):
                parts = process.split(None, 10)
                if len(parts) > 1:
                    process_id = int(parts[1])
                    matching_processes.append({
                        'processId': process_id,
                        'processString': process
                    })

        return JsonResponse(matching_processes, safe=False)

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to execute ps command'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)