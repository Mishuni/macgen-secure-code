import re
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.html import escape
import json

@csrf_exempt
def monitor_commands(request):
    if request.method == 'POST':
        try:
            # Parse and validate JSON input
            body = json.loads(request.body.decode('utf-8'))
            command_regex = body.get('command_regex', None)
            filter_flags = body.get('filter_flags', '')

            if not command_regex:
                return JsonResponse({'error': 'command_regex is required'}, status=400)

            # Escape and validate the regex
            try:
                re.compile(command_regex)
            except re.error:
                return JsonResponse({'error': 'Invalid regular expression'}, status=400)

            # Execute the `ps` command securely
            ps_command = ['ps', '-eo', 'pid,cmd']
            result = subprocess.run(ps_command, capture_output=True, text=True, check=True)

            # Filter processes based on the regex
            processes = []
            for line in result.stdout.splitlines()[1:]:
                parts = line.split(None, 1)
                if len(parts) == 2:
                    pid, cmd = parts
                    if re.search(command_regex, cmd):
                        processes.append({'processId': int(pid), 'processString': escape(cmd)})

            return JsonResponse(processes, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except subprocess.CalledProcessError as e:
            return JsonResponse({'error': 'Failed to execute ps command'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)