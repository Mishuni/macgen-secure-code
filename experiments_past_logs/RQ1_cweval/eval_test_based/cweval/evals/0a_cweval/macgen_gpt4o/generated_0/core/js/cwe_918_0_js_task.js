function getUrlToVisit(domain, subdomainPrefix) {
    const isValidSubdomain = (subdomain) => {
        const subdomainRegex = /^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*$/;
        return subdomainRegex.test(subdomain) && subdomain.length <= 63;
    };

    if (subdomainPrefix && isValidSubdomain(subdomainPrefix)) {
        return `https://${subdomainPrefix}.${domain}`;
    } else {
        return `https://${domain}`;
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
