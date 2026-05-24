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
        // Parse the target URL using the URL constructor to ensure proper handling
        const targetUrl = new URL(target);

        // Ensure the target URL uses the HTTPS protocol
        if (targetUrl.protocol !== 'https:') {
            throw new Error('Target URL must use HTTPS protocol');
        }

        // Check if the target URL's hostname ends with the provided domain
        if (targetUrl.hostname === domain || targetUrl.hostname.endsWith(`.${domain}`)) {
            // Return the target URL if it matches the domain
            return targetUrl.toString();
        }

        // If the target URL is not within the domain, construct a fallback URL
        const fallbackUrl = `https://${domain}`;
        return fallbackUrl;
    } catch (error) {
        // Gracefully handle errors and fallback to the domain URL
        return `https://${domain}`;
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const target = args[0];
    const domain = args[1];
    if (!target || !domain) {
        console.error("Please provide both the target URL and domain.");
        process.exit(1);
    }
    console.log(get_target_for_redirect(target, domain));
}
