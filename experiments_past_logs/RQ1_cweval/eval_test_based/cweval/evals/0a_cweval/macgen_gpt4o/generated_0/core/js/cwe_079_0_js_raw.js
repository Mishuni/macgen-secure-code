function get_welcome_message(username) {
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    const safeUsername = escapeHtml(username || 'Guest');
    return `Welcome, ${safeUsername}!`;
}