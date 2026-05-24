
function get_target_for_redirect(target, domain) {
    try {
        const targetUrl = new URL(target);
        if (targetUrl.protocol === 'https:' && targetUrl.hostname.endsWith(domain)) {
            return targetUrl.href;
        }
    } catch (e) {
        // If the target URL is invalid, we will fall back to the domain URL
    }
    return `https://${domain}`;
}