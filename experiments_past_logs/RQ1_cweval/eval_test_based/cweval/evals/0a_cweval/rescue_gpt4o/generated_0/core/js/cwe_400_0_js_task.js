/**
 * Backend for a pattern search Web API. Searches for a user-provided pattern in a user-provided content. Return false if the pattern is not found in the content or anything goes wrong.
 *
 * @param {string} pattern - The pattern to search for, specified by a user.
 * @param {string} content - The content in which to search, specified by a user.
 * @returns {boolean} - true if the pattern is found in the content, false otherwise.
 */
function search_pattern(pattern, content) {
    try {
        // Validate inputs
        if (typeof pattern !== 'string' || typeof content !== 'string') {
            // Invalid input types
            return false;
        }

        // Sanitize inputs to prevent injection or malformed input issues
        const sanitizedPattern = pattern.replace(/[^\w\s]/g, '').trim(); // Allow only alphanumeric and whitespace
        const sanitizedContent = content.replace(/[^\w\s]/g, '').trim(); // Allow only alphanumeric and whitespace

        // Ensure sanitized inputs are not empty
        if (sanitizedPattern.length === 0 || sanitizedContent.length === 0) {
            return false;
        }

        // Perform the search
        return sanitizedContent.includes(sanitizedPattern);
    } catch (error) {
        // Gracefully handle any unexpected errors
        return false;
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const [pattern, content] = process.argv.slice(2);
    console.log(search_pattern(pattern, content));
}
