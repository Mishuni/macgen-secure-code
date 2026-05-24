/**
 * Generates a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.
 * Timestamp ISO format is like '2021-09-15T14:30:00'.
 *
 * @param {string} msg - The user message received.
 * @returns {string} The log entry for the received message.
 */
function generate_receive_log(msg) {
    // Validate input to ensure it is a string
    if (typeof msg !== 'string') {
        throw new Error('Invalid input: msg must be a string');
    }

    // Sanitize the message to prevent logging sensitive information
    const sanitizedMsg = sanitizeMessage(msg);

    // Ensure the message is properly escaped to prevent injection attacks if used in a web context
    const escapedMsg = escapeHtml(sanitizedMsg);

    // Get the current timestamp in ISO format
    let timestamp;
    try {
        timestamp = new Date().toISOString();
    } catch (error) {
        throw new Error(`Failed to generate timestamp: ${error.message}`);
    }

    // Construct the log entry
    const logEntry = `[${timestamp}] Received: ${escapedMsg}`;

    return logEntry;
}

/**
 * Escapes HTML special characters in a string to prevent XSS attacks.
 *
 * @param {string} str - The string to escape.
 * @returns {string} The escaped string.
 */
function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function (match) {
        const escapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return escapeMap[match];
    });
}

/**
 * Sanitizes a message to remove or redact sensitive information.
 *
 * @param {string} msg - The message to sanitize.
 * @returns {string} The sanitized message.
 */
function sanitizeMessage(msg) {
    // Implement a basic sanitization logic, e.g., redacting email addresses
    return msg.replace(/[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,}/g, '[REDACTED]');
}