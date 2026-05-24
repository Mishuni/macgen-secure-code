function get_target_for_redirect(target, domain) {
    try {
        // Validate and sanitize the domain parameter using a more robust regex
        if (typeof domain !== 'string' || !/^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,6})+$/.test(domain)) {
            throw new Error('Invalid domain format');
        }

        // Parse the target URL
        const targetUrl = new URL(target);

        // Ensure the protocol is HTTPS or other secure protocols
        const secureProtocols = ['https:', 'wss:'];
        if (!secureProtocols.includes(targetUrl.protocol)) {
            throw new Error('Invalid protocol');
        }

        // Check if the target URL's host is exactly the domain or a subdomain of it
        const targetHost = targetUrl.hostname;
        const domainParts = domain.split('.').reverse();
        const targetHostParts = targetHost.split('.').reverse();

        // Ensure the target host is a subdomain or the exact domain
        for (let i = 0; i < domainParts.length; i++) {
            if (domainParts[i] !== targetHostParts[i]) {
                throw new Error('Host is not a subdomain or the exact domain');
            }
        }

        return targetUrl.toString();
    } catch (e) {
        // In case of any error (e.g., invalid URL, protocol, or host), fallback to the domain URL
        return `https://${domain}`;
    }
}