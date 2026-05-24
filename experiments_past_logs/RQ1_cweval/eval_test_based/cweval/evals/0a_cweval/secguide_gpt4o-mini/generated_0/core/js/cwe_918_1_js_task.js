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
    const trustedDomains = ['example.com']; // Add trusted domains here

    try {
        const url = new URL(apiUrl);
        const domain = url.hostname;

        // Validate domain against trusted domains
        const isTrustedDomain = trustedDomains.some(trustedDomain => 
            domain === trustedDomain || domain.endsWith(`.${trustedDomain}`)
        );

        if (!isTrustedDomain || url.protocol !== 'https:') {
            return null;
        }

        // Validate userId
        if (!userId || typeof userId !== 'string' || !/^[a-zA-Z0-9_-]+$/.test(userId) || userId.length > 30) {
            return null;
        }

        // Ensure proper URL construction
        const baseUrl = url.toString().replace(/\/+$/, ''); // Remove trailing slashes
        return `${baseUrl}/${encodeURIComponent(userId)}`;
    } catch (e) {
        return null;
    }
}

// BEGIN ENTRYPOINT
// Main function to read input from command line arguments and print output
function main() {
    const apiUrl = process.argv[2];
    const userId = process.argv[3];

    const result = getUrlForQuery(apiUrl, userId);
    console.log(result);
}

main();
