function generate_receive_log(msg) {
    const date = new Date();
    const timestampIsoFormat = date.toISOString();
    const sanitizedMsg = msg.replace(/[\r\n]/g, ' '); // Sanitize message to prevent log injection
    return `[${timestampIsoFormat}] Received: ${sanitizedMsg}`;
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2); // Get command-line arguments
    const msg = args[0] || ''; // Default to an empty message if none provided
    console.log(generate_receive_log(msg)); // Output the log entry
}
