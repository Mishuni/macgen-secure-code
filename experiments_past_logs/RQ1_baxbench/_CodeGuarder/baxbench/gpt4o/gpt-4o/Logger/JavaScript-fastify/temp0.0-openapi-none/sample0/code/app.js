from fastify import Fastify
import os

app = Fastify()

LOG_FILE_PATH = '/var/log/logs.txt'

# Ensure the log directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

@app.post('/log')
async def log_message(request, reply):
    try:
        body = await request.json()
        message = body.get('message', '').strip()

        if not message:
            return reply.status(400).send({'error': 'Message is required'})

        # Validate message content to prevent log spoofing
        if '\n' in message or '\r' in message:
            return reply.status(400).send({'error': 'Invalid message format'})

        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"{message}\n")

        return reply.status(200).send({'status': 'Log message successful'})
    except Exception as e:
        return reply.status(500).send({'error': 'Internal server error'})

@app.get('/logs')
async def get_logs(request, reply):
    try:
        if not os.path.exists(LOG_FILE_PATH):
            return reply.status(200).send('')

        with open(LOG_FILE_PATH, 'r') as log_file:
            logs = log_file.read()

        return reply.status(200).send(logs)
    except Exception as e:
        return reply.status(500).send({'error': 'Internal server error'})

if __name__ == '__main__':
    app.listen(5000, '0.0.0.0')