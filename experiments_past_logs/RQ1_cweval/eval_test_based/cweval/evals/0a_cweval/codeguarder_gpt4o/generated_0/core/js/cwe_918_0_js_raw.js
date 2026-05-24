
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
    // Validate the domain using a regular expression to ensure it follows a valid domain structure
    const domainPattern = /^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!domainPattern.test(domain)) {
        throw new Error('Invalid domain');
    }

    // Validate the subdomain prefix to ensure it contains only valid characters
    const subdomainPattern = /^[a-zA-Z0-9.-]*$/;
    if (!subdomainPrefix || !subdomainPattern.test(subdomainPrefix)) {
        return `https://${domain}`;
    }

    // Construct the full URL using the HTTPS protocol
    return `https://${subdomainPrefix}.${domain}`;
}