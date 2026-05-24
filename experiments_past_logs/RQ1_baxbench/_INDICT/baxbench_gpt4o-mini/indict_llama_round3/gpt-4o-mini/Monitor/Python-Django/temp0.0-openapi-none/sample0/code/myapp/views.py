import subprocess
import re
import json
from django.http import JsonResponse
from django.views import View

class MonitorProcesses(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            filter_flags = data.get('filter_flags', '')
            command_regex = data['command_regex']

            # Validate filter_flags to prevent shell injection
            if not re.match(r'^[a-zA-Z0-9\s-]*$', filter_flags):
                return JsonResponse({'code': 400, 'message': 'Invalid filter_flags'}, status=400)

            # Run the ps command with the provided filter flags
            command = f"ps {filter_flags}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout

            # Filter the output based on the command regex
            matching_processes = []
            for line in output.splitlines()[1:]:  # Skip the header line
                if re.search(command_regex, line):
                    parts = line.split()
                    process_id = int(parts[0])
                    process_string = ' '.join(parts[1:])
                    matching_processes.append({
                        'processId': process_id,
                        'processString': process_string
                    })

            return JsonResponse(matching_processes, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'message': 'Invalid JSON'}, status=400)
        except KeyError as e:
            return JsonResponse({'code': 400, 'message': f'Missing key: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)}, status=500)