
/**
 * Generates a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.
 * Timestamp ISO format is like '2021-09-15T14:30:00'.
 *
 * @param {string} msg - The user message received.
 * @returns {string} The log entry for the received message.
 */
function generate_receive_log(msg) {
    const sanitizeInput = (input) => {
        // Remove control characters and encode special characters to prevent injection attacks
        const sanitized = input.replace(/[\u0000-\u001F\u007F-\u009F]/g, '');
        return sanitized.replace(/[&<>"'`=\/]/g, (char) => {
            const charMap = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#x27;',
                '`': '&#x60;',
                '=': '&#x3D;',
                '/': '&#x2F;'
            };
            return charMap[char] || char;
        });
    };

    const sanitizedMsg = sanitizeInput(msg);
    const timestamp = new Date().toISOString();
    return `[${timestamp}] Received: ${sanitizedMsg}`;
}