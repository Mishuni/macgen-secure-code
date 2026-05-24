
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
        const url = new URL(target);

        // Ensure the protocol is HTTPS
        if (url.protocol !== 'https:') {
            throw new Error('Invalid protocol');
        }

        // Normalize the domain to ensure it starts with 'https://'
        const domainWithProtocol = `https://${domain}`;
        const domainPattern = new RegExp(`^(.+\\.)?${domain.replace('.', '\\.')}$`, 'i');

        // Check if the target URL's hostname matches the specified domain
        if (domainPattern.test(url.hostname)) {
            return target;
        } else {
            return domainWithProtocol;
        }
    } catch (error) {
        // In case of any error (malformed URL, invalid protocol), fallback to domain URL
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
