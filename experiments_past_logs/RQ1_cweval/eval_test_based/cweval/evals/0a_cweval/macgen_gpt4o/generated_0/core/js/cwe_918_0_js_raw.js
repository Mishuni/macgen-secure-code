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