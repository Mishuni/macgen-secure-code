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
    // Validate the API URL
    if (typeof apiUrl !== 'string' || !apiUrl.trim() || !isValidUrl(apiUrl)) {
        return null;
    }

    // Validate the user ID
    if (typeof userId !== 'string' || !userId.trim() || !isValidUserId(userId)) {
        return null;
    }

    // Construct and return the URL
    return `${apiUrl.replace(/\/+$/, '')}/${encodeURIComponent(userId)}`;
}

/**
 * Validates if a given string is a well-formed URL.
 *
 * @param {string} url - The URL to validate.
 * @returns {boolean} - True if the URL is valid, false otherwise.
 */
function isValidUrl(url) {
    try {
        const parsedUrl = new URL(url);
        return parsedUrl.protocol === 'http:' || parsedUrl.protocol === 'https:';
    } catch (e) {
        return false;
    }
}

/**
 * Validates the user ID to ensure it does not contain invalid characters.
 *
 * @param {string} userId - The user ID to validate.
 * @returns {boolean} - True if the user ID is valid, false otherwise.
 */
function isValidUserId(userId) {
    // Reject user IDs containing '/', '\', or null characters
    const invalidCharacters = /[\/\\\0]/;
    return !invalidCharacters.test(userId);
}