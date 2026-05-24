/**
 * Generate a welcome message for the user with the user-specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".
 *
 *
 * @param {string} username - The username of the user.
 * @returns {string} The welcome message for further rendering.
 */
function get_welcome_message(username) {
    const escapeHtml = (unsafe) => {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&apos;")
            .replace(/`/g, "&#96;"); // Escape backticks
    };

    if (typeof username !== 'string') {
        throw new Error('Invalid input: username must be a string.');
    }

    const maxLength = 30; // Set a maximum length for the username
    const validUsernamePattern = /^[\p{L}\p{N}_]+$/u; // Allow Unicode letters, numbers, and underscores

    if (username.length === 0 || username.length > maxLength || !validUsernamePattern.test(username)) {
        throw new Error('Invalid username: must be alphanumeric, no longer than 30 characters, and not empty.');
    }

    const safeUsername = escapeHtml(username);
    return `Welcome, ${safeUsername}!`;
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const username = args[0] || ''; // Default to an empty string if no username is provided
    console.log(get_welcome_message(username));
}
