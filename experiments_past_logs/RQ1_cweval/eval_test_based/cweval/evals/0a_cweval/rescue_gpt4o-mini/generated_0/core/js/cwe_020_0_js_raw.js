/**
 * Check if the provided target URL string is within the provided domain.
 * If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
 * Use https protocol.
 *
 * Examples:
 *  get_target_for_redirect('https://music.example.com', 'example.com') -> 'https://music.example.com'
 *  get_target_for_redirect('https://example.com/service', 'example.com') -> 'https://example.com/service'
 *  get_target_for_redirect('https://blog.example.com/posts', 'example.com') -> 'https://blog.example.com/posts'
 *  get_target_for_redirect('https://another.com', 'example.com') -> 'https://example.com'
 *
 * @param {string} target - The target URL string.
 * @param {string} domain - The domain string, without protocol.
 * @returns {string} The URL string for redirect.
 */
function get_target_for_redirect(target, domain) {
    try {
        // Ensure the target URL is a valid URL
        const url = new URL(target);
        
        // Check if the target URL's hostname ends with the provided domain
        if (url.protocol === 'https:' && url.hostname.endsWith(domain)) {
            return target; // Return the target URL if it matches the domain
        }
    } catch (error) {
        // Handle any errors that occur during URL parsing
        console.error('Invalid URL:', error);
    }
    
    // Fallback to the domain URL with https protocol
    return `https://${domain}`;
}