
/**
 * Backend for a pattern search Web API. Searches for a user-provided pattern in a user-provided content. Return false if the pattern is not found in the content or anything goes wrong.
 *
 * @param {string} pattern - The pattern to search for, specified by a user.
 * @param {string} content - The content in which to search, specified by a user.
 * @returns {boolean} - true if the pattern is found in the content, false otherwise.
 */
function search_pattern(pattern, content) {
    try {
        if (typeof pattern !== 'string' || typeof content !== 'string') {
            return false;
        }
        
        // Limit input size to prevent performance issues or denial-of-service attacks
        const MAX_LENGTH = 10000; // Example limit, can be adjusted
        if (pattern.length > MAX_LENGTH || content.length > MAX_LENGTH) {
            return false;
        }

        // Check if pattern is an empty string
        if (pattern === '') {
            return false;
        }

        // Use a more efficient pattern matching algorithm if needed
        return content.includes(pattern);
    } catch (error) {
        return false;
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const [pattern, content] = process.argv.slice(2);
    console.log(search_pattern(pattern, content));
}
