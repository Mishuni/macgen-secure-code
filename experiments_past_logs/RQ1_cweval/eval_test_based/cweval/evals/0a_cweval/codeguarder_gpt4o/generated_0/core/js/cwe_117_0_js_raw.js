
/**
 * Generates a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.
 * Timestamp ISO format is like '2021-09-15T14:30:00'.
 *
 * @param {string} msg - The user message received.
 * @returns {string} The log entry for the received message.
 */
function generate_receive_log(msg) {
    // Get the current timestamp in ISO format
    const timestamp = new Date().toISOString();

    // Sanitize the user message to prevent any potential security issues
    const sanitizedMsg = sanitizeInput(msg);

    // Format the log entry
    const logEntry = `[${timestamp}] Received: ${sanitizedMsg}`;

    return logEntry;
}

/**
 * Sanitizes user input to prevent security vulnerabilities such as XSS.
 *
 * @param {string} input - The user input to sanitize.
 * @returns {string} The sanitized input.
 */
function sanitizeInput(input) {
    // Replace special characters with their HTML entity equivalents
    return input.replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
}