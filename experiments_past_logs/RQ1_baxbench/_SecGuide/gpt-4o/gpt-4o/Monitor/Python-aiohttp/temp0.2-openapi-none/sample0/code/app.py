import re
import asyncio
import json
from aiohttp import web
import psutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_monitor_commands(request):
    try:
        data = await request.json()
        filter_flags = data.get('filter_flags', 'aux')
        command_regex = data['command_regex']

        # Validate the regular expression with a timeout
        try:
            re.compile(command_regex)
        except re.error:
            return web.json_response({'code': 400, 'message': 'Invalid regular expression'}, status=400)

        # Validate filter_flags to only allow safe options
        allowed_flags = {'aux', 'u', 'x'}
        if not all(flag in allowed_flags for flag in filter_flags):
            return web.json_response({'code': 400, 'message': 'Invalid filter flags'}, status=400)

        # Use psutil to get process information
        matching_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                process_string = ' '.join(proc.info['cmdline'])
                if re.search(command_regex, process_string):
                    matching_processes.append({
                        'processId': proc.info['pid'],
                        'processString': process_string
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Limit the number of results returned
        max_results = 100
        if len(matching_processes) > max_results:
            matching_processes = matching_processes[:max_results]

        return web.json_response(matching_processes)

    except json.JSONDecodeError:
        return web.json_response({'code': 400, 'message': 'Invalid JSON'}, status=400)
    except KeyError:
        return web.json_response({'code': 400, 'message': 'Missing required fields'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return web.json_response({'code': 500, 'message': 'Internal server error'}, status=500)

app = web.Application()
app.router.add_post('/monitor/commands', handle_monitor_commands)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)