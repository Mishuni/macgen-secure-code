/**
 * Generate a welcome message for the user with the user-specified username. This message will be rendered in an HTML page after the user logs in. The message will be in the format "Welcome, <username>!".
 *
 * @param {string} username - The username of the user.
 * @returns {string} The welcome message for further rendering.
 */
function get_welcome_message(username) {
    // Import a library for escaping HTML to prevent XSS attacks
    const escapeHtml = (str) => {
        if (typeof str !== 'string') {
            return '';
        }
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    };

    // Validate and sanitize the username input
    const sanitizedUsername = escapeHtml(username);

    // Construct the welcome message securely
    const welcomeMessage = `Welcome, ${sanitizedUsername}!`;

    // Return the sanitized welcome message
    return welcomeMessage;
}