const htmlEscape = require('escape-html');

/**
 * Generate a welcome message for the user with the user-specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".
 *
 * @param {string} username - The username of the user.
 * @returns {string} The welcome message for further rendering.
 */
function get_welcome_message(username) {
    // Validate the username input
    if (typeof username !== 'string') {
        throw new Error('Invalid input: username must be a string');
    }
    if (username.length < 1 || username.length > 50) {
        throw new Error('Invalid input: username must be between 1 and 50 characters');
    }
    if (!/^[\w-]+$/.test(username)) { // Allow alphanumeric, underscores, and hyphens
        throw new Error('Invalid input: username contains invalid characters');
    }

    // Escape the username to prevent XSS attacks
    const safeUsername = htmlEscape(username);
    return `Welcome, ${safeUsername}!`;
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const username = args[0] || ''; // Default to an empty string if no username is provided
    console.log(get_welcome_message(username));
}
