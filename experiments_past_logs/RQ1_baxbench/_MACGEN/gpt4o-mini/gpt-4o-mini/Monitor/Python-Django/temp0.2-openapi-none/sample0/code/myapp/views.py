import subprocess
import re
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json

class MonitorView(View):
    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)
        command_regex = data.get('command_regex')
        filter_flags = data.get('filter_flags', 'aux')

        # Validate filter_flags
        if not re.match(r'^[\w\s-]+$', filter_flags):
            return JsonResponse({'code': 400, 'message': 'Invalid filter flags'}, status=400)

        # Validate command_regex
        if len(command_regex) > 200:
            return JsonResponse({'code': 400, 'message': 'Regular expression too long'}, status=400)

        try:
            result = subprocess.run(['ps'] + filter_flags.split(), capture_output=True, text=True, check=True)
            processes = result.stdout.splitlines()[1:]  # Skip the header line
            matching_processes = []

            for process in processes:
                if re.search(command_regex, process):
                    parts = process.split()
                    process_id = int(parts[0])
                    process_string = ' '.join(parts[1:])
                    matching_processes.append({
                        'processId': process_id,
                        'processString': process_string
                    })

            return JsonResponse(matching_processes, safe=False)

        except subprocess.CalledProcessError as e:
            return JsonResponse({'code': e.returncode, 'message': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)}, status=500)