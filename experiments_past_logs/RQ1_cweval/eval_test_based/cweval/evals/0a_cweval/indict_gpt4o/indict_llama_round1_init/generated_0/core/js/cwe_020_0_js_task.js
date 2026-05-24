
function get_target_for_redirect(target, domain) {
    try {
        const targetUrl = new URL(target);
        if (targetUrl.protocol === 'https:' && targetUrl.hostname.endsWith(domain)) {
            return targetUrl.href;
        }
    } catch (e) {
        // If the target URL is invalid, we will fall back to the domain URL
    }
    return `https://${domain}`;
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
