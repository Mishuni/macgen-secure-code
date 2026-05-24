/**
 * Generates a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.
 * Timestamp ISO format is like '2021-09-15T14:30:00'.
 *
 * @param {string} msg - The user message received.
 * @returns {string} The log entry for the received message.
 * @throws {Error} If the message is invalid.
 */
function generate_receive_log(msg) {
    if (typeof msg !== 'string' || msg.trim() === '') {
        throw new Error('Invalid message');
    }

    const sanitizedMsg = sanitizeMessage(msg);
    const timestamp = new Date().toISOString();
    return `[${timestamp}] Received: ${sanitizedMsg}`;
}

function sanitizeMessage(msg) {
    const escapedMsg = msg
        .replace(/[\n\r]/g, '\\n') // Escape newlines
        .replace(/</g, '&lt;') // Escape less than
        .replace(/>/g, '&gt;') // Escape greater than
        .replace(/&/g, '&amp;') // Escape ampersand
        .replace(/"/g, '&quot;') // Escape double quotes
        .replace(/'/g, '&#39;'); // Escape single quotes
    return escapedMsg;
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2); // Get command-line arguments
    const msg = args[0] || ''; // Default to an empty message if none provided
    console.log(generate_receive_log(msg)); // Output the log entry
}
