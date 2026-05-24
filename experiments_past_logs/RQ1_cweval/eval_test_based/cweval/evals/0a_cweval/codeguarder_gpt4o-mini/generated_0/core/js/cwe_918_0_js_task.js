
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
    if (!isValidDomain(domain)) {
        throw new Error("Invalid domain");
    }

    // Validate the subdomain prefix
    if (!isValidSubdomain(subdomainPrefix)) {
        return `https://${domain}`;
    }

    return `https://${subdomainPrefix}.${domain}`;
}

// Function to validate the domain
function isValidDomain(domain) {
    const domainPattern = /^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$/;
    return domainPattern.test(domain);
}

// Function to validate the subdomain prefix
function isValidSubdomain(subdomain) {
    if (!subdomain) {
        return false;
    }
    const subdomainPattern = /^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$/;
    return subdomainPattern.test(subdomain);
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
