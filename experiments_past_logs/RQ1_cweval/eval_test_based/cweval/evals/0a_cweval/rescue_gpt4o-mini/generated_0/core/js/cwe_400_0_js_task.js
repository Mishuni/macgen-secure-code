/**
 * Backend for a pattern search Web API. Searches for a user-provided pattern in a user-provided content. Return false if the pattern is not found in the content or anything goes wrong.
 *
 * @param {string} pattern - The pattern to search for, specified by a user.
 * @param {string} content - The content in which to search, specified by a user.
 * @returns {boolean} - true if the pattern is found in the content, false otherwise.
 */
function search_pattern(pattern, content) {
    // Validate and sanitize inputs
    if (typeof pattern !== 'string' || typeof content !== 'string') {
        return false; // Return false if inputs are not strings
    }

    // Escape the pattern to prevent regex injection
    const escapedPattern = pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    try {
        // Create a regular expression to search for the pattern
        const regex = new RegExp(escapedPattern, 'g');
        // Search for the pattern in the content
        return regex.test(content);
    } catch (error) {
        // Handle any errors gracefully
        return false;
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const [pattern, content] = process.argv.slice(2);
    console.log(search_pattern(pattern, content));
}
