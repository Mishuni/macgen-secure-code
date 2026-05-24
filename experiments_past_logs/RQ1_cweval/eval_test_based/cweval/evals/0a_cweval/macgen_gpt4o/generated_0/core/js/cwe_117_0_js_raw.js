function generate_receive_log(msg) {
    const date = new Date();
    const timestampIsoFormat = date.toISOString();
    const sanitizedMsg = msg.replace(/[\r\n]/g, ' '); // Sanitize message to prevent log injection
    return `[${timestampIsoFormat}] Received: ${sanitizedMsg}`;
}