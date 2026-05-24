/**
 * Generates a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.
 * Timestamp ISO format is like '2021-09-15T14:30:00'.
 *
 * @param {string} msg - The user message received.
 * @returns {string} The log entry for the received message.
 */
function generate_receive_log(msg) {
    // Import a library for sanitization and escaping
    const DOMPurify = require('dompurify'); // Ensure this library is installed in your environment

    // Validate and sanitize the input message
    if (typeof msg !== 'string') {
        throw new Error('Invalid input: msg must be a string');
    }
    const sanitizedMsg = DOMPurify.sanitize(msg);

    // Get the current timestamp in ISO format
    const timestamp = new Date().toISOString();

    // Construct the log entry securely
    const logEntry = `[${timestamp}] Received: ${sanitizedMsg}`;

    // Return the log entry
    return logEntry;
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2); // Get command-line arguments
    const msg = args[0] || ''; // Default to an empty message if none provided
    console.log(generate_receive_log(msg)); // Output the log entry
}
