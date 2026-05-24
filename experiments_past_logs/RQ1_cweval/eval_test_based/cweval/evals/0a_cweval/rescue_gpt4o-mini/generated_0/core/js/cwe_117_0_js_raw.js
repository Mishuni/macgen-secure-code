/**
 * Generates a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.
 * Timestamp ISO format is like '2021-09-15T14:30:00'.
 *
 * @param {string} msg - The user message received.
 * @returns {string} The log entry for the received message.
 */
function generate_receive_log(msg) {
    // Importing the necessary library for escaping
    const escape = require('escape-html'); // Assuming escape-html is used for sanitization

    // Get the current timestamp in ISO format
    const timestamp = new Date().toISOString();

    // Sanitize the user message to prevent XSS
    const sanitizedMsg = escape(msg);

    // Generate the log entry
    return `[${timestamp}] Received: ${sanitizedMsg}`;
}