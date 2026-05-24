
function get_target_for_redirect(target, domain) {
    // Validate input parameters
    if (typeof target !== 'string' || typeof domain !== 'string') {
        throw new Error('Invalid input: target and domain must be strings.');
    }

    // Ensure the target URL uses HTTPS
    const urlPattern = new RegExp('^https://');
    if (!urlPattern.test(target)) {
        throw new Error('Invalid URL: target must use HTTPS protocol.');
    }

    // Create a URL object to easily extract the hostname
    let targetUrl;
    try {
        targetUrl = new URL(target);
    } catch (e) {
        throw new Error('Invalid URL: Unable to parse target URL.');
    }

    // Check if the target URL's hostname ends with the provided domain
    const domainPattern = new RegExp(`(${domain})$`);
    if (domainPattern.test(targetUrl.hostname)) {
        return target; // Return the target URL if it matches the domain
    }

    // Fallback to the domain URL
    return `https://${domain}`;
}