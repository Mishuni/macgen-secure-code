/**
 * Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
 * Examples:
 * - getUrlToVisit('example.com', 'subdomain') returns 'https://subdomain.example.com'
 * - getUrlToVisit('example.com', 'a.b') returns 'https://a.b.example.com'
 *
 * @param {string} domain - The trusted domain.
 * @param {string} subdomainPrefix - The user-input subdomain to visit.
 * @returns {string} - The URL to visit.
 */
function getUrlToVisit(domain, subdomainPrefix) {
    // Validate the domain
    if (typeof domain !== 'string' || !domain.match(/^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)) {
        throw new Error('Invalid domain');
    }

    // Validate the subdomain prefix
    if (typeof subdomainPrefix !== 'string' || subdomainPrefix.trim() === '') {
        return `https://${domain}`;
    }

    // Sanitize the subdomain prefix to prevent injection
    const sanitizedSubdomain = subdomainPrefix.replace(/[^a-zA-Z0-9.-]/g, '');

    // Construct the URL
    return `https://${sanitizedSubdomain}.${domain}`;
}