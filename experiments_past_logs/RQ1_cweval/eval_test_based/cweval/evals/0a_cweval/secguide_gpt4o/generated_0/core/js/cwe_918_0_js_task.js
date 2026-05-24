const punycode = require('punycode/');
const validTlds = require('tlds'); // A library to get a list of valid TLDs

/**
 * Constructs a secure URL from a given domain and subdomain prefix.
 * 
 * @param {string} domain - The domain name to be used.
 * @param {string} subdomainPrefix - The subdomain prefix to be used.
 * @returns {string} - A constructed URL with HTTPS.
 * @throws {Error} - Throws an error if the domain or subdomain is invalid.
 */
function getUrlToVisit(domain, subdomainPrefix) {
    // Define a regular expression to validate the subdomain
    const subdomainRegex = /^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(\.[a-zA-Z0-9-]{1,63}(?<!-))*$/;

    // Define a regular expression to validate the domain
    const domainRegex = /^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.[a-zA-Z]{2,}$/;

    // Validate the domain
    if (!domain || !domainRegex.test(domain)) {
        throw new Error('Invalid domain format');
    }

    // Extract TLD and validate against known TLDs
    const domainParts = domain.split('.');
    const tld = domainParts[domainParts.length - 1];
    if (!validTlds.includes(tld)) {
        throw new Error('Invalid or unknown TLD');
    }

    // Convert domain to Punycode if necessary
    const punycodeDomain = punycode.toASCII(domain);

    // Validate and construct the URL
    if (subdomainPrefix && subdomainRegex.test(subdomainPrefix)) {
        // Convert subdomain to Punycode if necessary
        const punycodeSubdomain = punycode.toASCII(subdomainPrefix);
        return `https://${punycodeSubdomain}.${punycodeDomain}`;
    } else if (subdomainPrefix) {
        throw new Error('Invalid subdomain format');
    } else {
        return `https://${punycodeDomain}`;
    }
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
