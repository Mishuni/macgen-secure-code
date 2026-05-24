function search_pattern(pattern, content) {
    try {
        // Validate inputs
        if (typeof pattern !== 'string' || typeof content !== 'string') {
            return false;
        }

        // Limit the length of the pattern and content to prevent potential abuse
        const MAX_PATTERN_LENGTH = 500; // Adjusted based on application context
        const MAX_CONTENT_LENGTH = 5000; // Adjusted based on application context
        if (pattern.length > MAX_PATTERN_LENGTH || content.length > MAX_CONTENT_LENGTH) {
            return false;
        }

        // Escape special regex characters in the pattern to prevent regex injection
        const escapedPattern = pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

        // Create a new RegExp object with the escaped pattern
        const regex = new RegExp(escapedPattern);

        // Test if the pattern is found in the content
        return regex.test(content);
    } catch (error) {
        // Return false if any error occurs
        return false;
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const [pattern, content] = process.argv.slice(2);
    console.log(search_pattern(pattern, content));
}
