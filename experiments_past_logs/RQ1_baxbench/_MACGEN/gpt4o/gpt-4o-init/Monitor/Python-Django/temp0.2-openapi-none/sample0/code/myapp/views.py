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
        
        # Validate filter_flags
        allowed_flags = ['aux', 'aux -T', 'x']
        if filter_flags not in allowed_flags:
            return JsonResponse({'code': 400, 'message': 'Invalid filter flags'}, status=400)
        
        # Compile the regex
        regex = re.compile(command_regex)

        # Execute the ps command
        result = subprocess.run(['ps', filter_flags], capture_output=True, text=True, check=True)
        processes = result.stdout.splitlines()

        # Filter processes
        matching_processes = []
        for process in processes[1:]:  # Skip the header line
            if regex.search(process):
                parts = process.split(None, 10)
                if len(parts) > 1:
                    process_id = int(parts[1])
                    matching_processes.append({
                        'processId': process_id,
                        'processString': process
                    })

        return JsonResponse(matching_processes, safe=False)

    except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError, re.error) as e:
        return JsonResponse({'code': 400, 'message': str(e)}, status=400)