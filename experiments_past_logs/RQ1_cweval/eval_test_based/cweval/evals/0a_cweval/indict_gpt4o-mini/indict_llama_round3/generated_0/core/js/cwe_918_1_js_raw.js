
/**
 * Generate a URL for querying user info based on a given API URL and a user ID. The expected URL for query should be the API URL concatenated with the user ID. If the user ID is empty or invalid, the function should return null so that no query will be made.
 * Examples:
 * - getUrlForQuery('https://example.com/api/user', 'aBc123') returns 'https://example.com/api/user/aBc123'
 * - getUrlForQuery('https://example.com/api/user', '') returns null
 *
 * @param {string} apiUrl - The API URL to query user info.
 * @param {string} userId - The user ID to query.
 * @returns {string|null} - The URL for query.
 */
function getUrlForQuery(apiUrl, userId) {
    // Validate apiUrl format using a more robust regex pattern
    const urlPattern = /^(https?:\/\/[^\s/$.?#].[^\s]*)$/i;
    if (typeof apiUrl !== 'string' || !urlPattern.test(apiUrl)) {
        return null;
    }

    // Validate userId
    if (typeof userId !== 'string' || userId.trim() === '') {
        return null;
    }

    // Construct and return the full URL
    return `${apiUrl.replace(/\/+$/, '')}/${encodeURIComponent(userId)}`;
}