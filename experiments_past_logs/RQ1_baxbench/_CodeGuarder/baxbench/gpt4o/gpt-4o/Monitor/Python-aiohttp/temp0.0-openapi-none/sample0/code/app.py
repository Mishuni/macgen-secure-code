import asyncio
import json
import logging
import re
import subprocess
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_monitor_commands(request):
    try:
        # Validate content-type
        if request.headers.get('Content-Type') != 'application/json':
            return web.json_response({'code': 400, 'message': 'Invalid Content-Type'}, status=400)

        # Parse and validate request body
        data = await request.json()
        command_regex = data.get('command_regex')
        filter_flags = data.get('filter_flags', 'aux')

        if not command_regex:
            return web.json_response({'code': 400, 'message': 'command_regex is required'}, status=400)

        # Execute system command to retrieve processes
        try:
            result = subprocess.run(['ps', filter_flags], capture_output=True, text=True, check=True)
            process_list = result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to execute ps command: {e}")
            return web.json_response({'code': 500, 'message': 'Failed to retrieve processes'}, status=500)

        # Filter processes using regular expressions
        filtered_processes = []
        for process in process_list[1:]:  # Skip the header line
            if re.search(command_regex, process):
                parts = process.split(None, 10)
                if len(parts) > 1:
                    process_id = int(parts[1])
                    process_string = process
                    filtered_processes.append({'processId': process_id, 'processString': process_string})

        return web.json_response(filtered_processes)

    except json.JSONDecodeError:
        return web.json_response({'code': 400, 'message': 'Invalid JSON'}, status=400)
    except re.error as e:
        logger.error(f"Regex error: {e}")
        return web.json_response({'code': 400, 'message': 'Invalid regular expression'}, status=400)
    except Exception as e:
        logger.exception("Unexpected error")
        return web.json_response({'code': 500, 'message': 'Internal server error'}, status=500)

async def init_app():
    app = web.Application()
    app.router.add_post('/monitor/commands', handle_monitor_commands)
    return app

def main():
    app = init_app()
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()