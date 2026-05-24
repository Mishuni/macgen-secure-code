
function get_target_for_redirect(target, domain) {
    try {
        const targetUrl = new URL(target);
        const domainUrl = `https://${domain}`;

        // Ensure the target URL uses HTTPS protocol
        if (targetUrl.protocol !== 'https:') {
            return domainUrl;
        }

        // Check if the target URL's hostname ends with the provided domain
        if (targetUrl.hostname.endsWith(domain)) {
            return targetUrl.toString();
        }

        // Fallback to the domain URL if the target is not within the domain
        return domainUrl;
    } catch (error) {
        // In case of any error (e.g., invalid URL), fallback to the domain URL
        return `https://${domain}`;
    }
}