function get_target_for_redirect(target, domain) {
    const allowedDomains = new Set([
        'example.com',
        'sub.example.com'
        // Add other trusted domains as needed
    ]);

    const url = new URL(target);

    // Enforce HTTPS for all redirects
    if (url.protocol !== 'https:') {
        return 'https://' + domain;
    }

    const targetDomain = url.hostname;

    // Strict domain validation
    const isValidDomain = allowedDomains.has(targetDomain) || 
                          (targetDomain.endsWith('.' + domain) && 
                          allowedDomains.has(domain));

    // Return the target if valid, otherwise redirect to the default domain
    if (isValidDomain) {
        return target;
    } else {
        return 'https://' + domain;
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const target = args[0];
    const domain = args[1];
    if (!target || !domain) {
        console.error("Please provide both the target URL and domain.");
        process.exit(1);
    }
    console.log(get_target_for_redirect(target, domain));
}
