import re
import subprocess
from aiohttp import web
import json

async def handle_monitor_commands(request):
    try:
        data = await request.json()
        filter_flags = data.get('filter_flags', '')
        command_regex = data['command_regex']
        
        # Run the ps command
        ps_command = ['ps'] + filter_flags.split()
        result = subprocess.run(ps_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            return web.json_response({'code': 500, 'message': 'Failed to execute ps command'}, status=500)
        
        # Parse the output
        lines = result.stdout.strip().split('\n')
        header = lines[0]
        process_list = lines[1:]
        
        # Dynamically find the index of the PID and CMD columns
        header_parts = header.split()
        pid_index = header_parts.index('PID')
        cmd_index = header_parts.index('CMD') if 'CMD' in header_parts else -1
        
        if cmd_index == -1:
            return web.json_response({'code': 500, 'message': 'CMD column not found in ps output'}, status=500)
        
        matching_processes = []
        
        # Validate and compile the regex pattern
        try:
            pattern = re.compile(command_regex)
        except re.error:
            return web.json_response({'code': 400, 'message': 'Invalid regular expression'}, status=400)
        
        for process in process_list:
            parts = process.split(None, len(header_parts) - 1)
            cmd_string = parts[cmd_index]
            
            if pattern.search(cmd_string):
                process_id = int(parts[pid_index])
                matching_processes.append({
                    'processId': process_id,
                    'processString': process
                })
        
        return web.json_response(matching_processes)
    
    except KeyError:
        return web.json_response({'code': 400, 'message': 'Invalid request body'}, status=400)
    except Exception as e:
        return web.json_response({'code': 500, 'message': str(e)}, status=500)

app = web.Application()
app.router.add_post('/monitor/commands', handle_monitor_commands)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)