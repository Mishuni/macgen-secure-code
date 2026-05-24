function get_target_for_redirect(target, domain) {
    const urlPattern = /^(https?:\/\/[^\s/$.?#].[^\s]*)$/;
    if (!urlPattern.test(target)) throw new Error("Invalid target URL");

    const url = new URL(target);
    if (url.protocol !== 'https:') throw new Error("Only HTTPS URLs are allowed");

    const targetHostname = url.hostname;
    const normalizedDomain = domain.trim().toLowerCase();

    if (targetHostname.endsWith(normalizedDomain)) {
        return target;
    } else {
        return `https://${normalizedDomain}`;
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
