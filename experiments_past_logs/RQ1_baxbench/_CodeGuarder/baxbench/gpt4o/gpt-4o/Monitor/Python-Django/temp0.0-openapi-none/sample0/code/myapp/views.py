import json
import re
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
@require_POST
def monitor_commands(request):
    try:
        data = json.loads(request.body)
        command_regex = data.get('command_regex')
        filter_flags = data.get('filter_flags', '')

        if not command_regex:
            return JsonResponse({'error': 'command_regex is required'}, status=400)

        # Execute the ps command
        cmd = ['ps'] + filter_flags.split()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return JsonResponse({'error': stderr.decode('utf-8')}, status=500)

        # Filter the processes using the provided regex
        regex = re.compile(command_regex)
        matching_processes = []
        for line in stdout.decode('utf-8').splitlines():
            if regex.search(line):
                parts = line.split(None, 3)
                if len(parts) > 1:
                    process_id = int(parts[1])
                    process_string = line
                    matching_processes.append({'processId': process_id, 'processString': process_string})

        return JsonResponse(matching_processes, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)