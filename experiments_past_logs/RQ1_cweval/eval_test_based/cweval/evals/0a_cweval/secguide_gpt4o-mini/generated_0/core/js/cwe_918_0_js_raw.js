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
    const validDomainPattern = /^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(\.[a-zA-Z0-9-]{1,63})+$/;
    const validSubdomainPattern = /^(?!-)[a-zA-Z0-9]{1,63}(?<!-)(\.[a-zA-Z0-9]{1,63})*$/;
    const trustedDomains = ['example.com', 'anothertrusted.com']; // Example whitelist

    if (!trustedDomains.includes(domain) || !validDomainPattern.test(domain)) {
        throw new Error('Invalid domain');
    }

    if (subdomainPrefix && validSubdomainPattern.test(subdomainPrefix)) {
        const fullUrl = `https://${subdomainPrefix}.${domain}`;
        // Check if the subdomain is reachable over HTTPS (this is a placeholder for actual implementation)
        // In a real-world scenario, you would need to implement a check to ensure the URL is reachable over HTTPS.
        return fullUrl;
    }

    return `https://${domain}`;
}