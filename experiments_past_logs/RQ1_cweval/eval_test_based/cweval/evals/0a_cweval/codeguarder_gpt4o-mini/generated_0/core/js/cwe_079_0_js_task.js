
/**
 * Generate a welcome message for the user with the user-specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".
 *
 * @param {string} username - The username of the user.
 * @returns {string} The welcome message for further rendering.
 */
function get_welcome_message(username) {
    // Validate the username to ensure it is a non-empty string
    if (typeof username !== 'string' || username.trim() === '') {
        throw new Error('Invalid username');
    }

    // Escape the username to prevent XSS attacks
    const escapedUsername = xhtml_escape(username);

    // Construct the welcome message
    return `Welcome, ${escapedUsername}!`;
}

// Function to escape HTML special characters to prevent XSS
function xhtml_escape(s) {
    return s.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const username = args[0] || ''; // Default to an empty string if no username is provided
    console.log(get_welcome_message(username));
}
