
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
        const targetUrl = new URL(target);
        const targetHostname = targetUrl.hostname;

        // Check if the target hostname is exactly the domain or a valid subdomain
        const domainPattern = new RegExp(`(^|\\.)${domain.replace('.', '\\.')}$`);
        if (targetUrl.protocol === 'https:' && domainPattern.test(targetHostname)) {
            return targetUrl.href;
        }
    } catch (e) {
        // If the target URL is invalid, we will fall back to the domain URL
    }
    return `https://${domain}`;
}