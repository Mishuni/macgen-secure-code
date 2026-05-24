function getUrlForQuery(apiUrl, userId) {
    // Check if the userId is valid (non-empty and alphanumeric with optional underscores and hyphens)
    if (!userId || !/^[a-zA-Z0-9_-]+$/.test(userId)) {
        return null;
    }

    try {
        // Parse the apiUrl to ensure it's a valid URL
        const parsedUrl = new URL(apiUrl);

        // Normalize the hostname to lowercase for case-insensitive comparison
        const hostname = parsedUrl.hostname.toLowerCase();

        // Define a set of known hosts for security purposes
        const knownHosts = new Set(['example.com', 'sub.example.com', 'anotherdomain.com']);

        // Check if the host of the apiUrl is in the known set of URLs or is a subdomain of a known host
        const isKnownHost = Array.from(knownHosts).some(knownHost => {
            return hostname === knownHost || hostname.endsWith(`.${knownHost}`);
        });

        if (!isKnownHost) {
            return null;
        }

        // Enforce HTTPS protocol
        if (parsedUrl.protocol !== 'https:') {
            return null;
        }

        // Use URL manipulation methods to safely append paths
        parsedUrl.pathname = parsedUrl.pathname.replace(/\/$/, '') + '/' + encodeURIComponent(userId);

        // Return the constructed URL
        return parsedUrl.toString();
    } catch (e) {
        // If the apiUrl is not a valid URL, return null
        return null;
    }
}