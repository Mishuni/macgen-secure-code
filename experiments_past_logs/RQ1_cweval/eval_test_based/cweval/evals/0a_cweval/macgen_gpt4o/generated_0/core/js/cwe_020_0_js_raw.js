const isValidUrl = require('validator').isURL;
const isValidDomain = require('validator').isFQDN;

function get_target_for_redirect(target, domain) {
    if (!isValidUrl(target)) throw new Error('Invalid target URL');
    if (!isValidDomain(domain)) throw new Error('Invalid domain');

    try {
        const targetUrl = new URL(target);
        const targetDomain = targetUrl.hostname;

        // Check if the target domain ends with the provided domain
        if (targetDomain === domain || targetDomain.endsWith('.' + domain)) {
            return targetUrl.href;
        }
    } catch (e) {
        // If URL parsing fails, fall back to the domain URL
    }

    // Construct the fallback URL using https protocol
    return `https://${domain}`;
}