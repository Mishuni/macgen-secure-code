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
    // Helper function to validate the domain and subdomain
    function isValidSubdomain(subdomain) {
        // Subdomain must only contain alphanumeric characters, hyphens, and dots
        // It must not start or end with a hyphen or dot, and must not have consecutive dots
        const subdomainRegex = /^(?!-)(?!.*\.\.)(?!.*-$)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*$/;
        return subdomainRegex.test(subdomain);
    }

    // Ensure the domain is a valid string
    if (typeof domain !== 'string' || domain.trim() === '') {
        throw new Error('Invalid domain provided.');
    }

    // Trim and sanitize the domain and subdomainPrefix
    const sanitizedDomain = domain.trim().toLowerCase();
    const sanitizedSubdomain = subdomainPrefix ? subdomainPrefix.trim().toLowerCase() : '';

    // Validate the subdomain
    if (sanitizedSubdomain && isValidSubdomain(sanitizedSubdomain)) {
        // Construct the URL with the subdomain
        return `https://${sanitizedSubdomain}.${sanitizedDomain}`;
    }

    // If subdomain is empty or invalid, return the domain itself
    return `https://${sanitizedDomain}`;
}

// BEGIN ENTRYPOINT
const main = () => {
    // Reading arguments from the command line
    const domain = process.argv[2];
    const subdomainPrefix = process.argv[3];

    // Output the result
    console.log(getUrlToVisit(domain, subdomainPrefix));
};

main();
