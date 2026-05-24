
function getUrlToVisit(domain, subdomainPrefix) {
    // Regular expression to validate subdomain
    const subdomainRegex = /^[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*$/;

    // Check if the subdomainPrefix is valid
    if (subdomainPrefix && subdomainRegex.test(subdomainPrefix)) {
        return `https://${subdomainPrefix}.${domain}`;
    }

    // Return the domain itself if subdomainPrefix is empty or invalid
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
