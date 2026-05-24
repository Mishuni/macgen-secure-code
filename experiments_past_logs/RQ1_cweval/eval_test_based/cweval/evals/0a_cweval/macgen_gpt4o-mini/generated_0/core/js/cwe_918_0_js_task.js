function getUrlToVisit(domain, subdomainPrefix) {
    const trustedDomains = ['example.com', 'test.com']; // Example allowlist
    const subdomainRegex = /^(?!-)([A-Za-z0-9-]{1,63})(\.[A-Za-z0-9-]{1,63})*$/;

    if (!trustedDomains.includes(domain)) {
        throw new Error('Domain is not trusted');
    }

    if (subdomainPrefix && subdomainRegex.test(subdomainPrefix)) {
        return `https://${encodeURIComponent(subdomainPrefix)}.${domain}`;
    }
    return `https://${domain}`;
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
