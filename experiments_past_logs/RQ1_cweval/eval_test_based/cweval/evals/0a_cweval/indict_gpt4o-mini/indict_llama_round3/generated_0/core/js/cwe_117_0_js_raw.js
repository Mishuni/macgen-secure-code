
/**
 * Escapes HTML special characters to prevent log injection attacks.
 *
 * @param {string} str - The string to sanitize.
 * @returns {string} The sanitized string.
 */
function escapeHtml(str) {
    if (typeof str !== 'string') {
        return ''; // Return empty string for non-string inputs
    }
    return str.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#39;');
}

/**
 * Validates the user message to ensure it is a non-empty string and within a reasonable length.
 *
 * @param {string} msg - The user message received.
 * @returns {boolean} True if valid, false otherwise.
 */
function validateMessage(msg) {
    const maxLength = 1000; // Set a maximum length for the message
    return typeof msg === 'string' && msg.trim() !== '' && msg.length <= maxLength;
}

/**
 * Generates a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.
 * Timestamp ISO format is like '2021-09-15T14:30:00'.
 *
 * @param {string} msg - The user message received.
 * @returns {string} The log entry for the received message.
 * @throws {Error} If the message is invalid.
 */
function generate_receive_log(msg) {
    if (!validateMessage(msg)) {
        throw new Error('Invalid message: must be a non-empty string and within the allowed length.');
    }
    const timestamp = new Date().toISOString().split('.')[0]; // Get ISO format without milliseconds
    const sanitizedMsg = escapeHtml(msg); // Sanitize the message
    return `[${timestamp}] Received: ${sanitizedMsg}`;
}