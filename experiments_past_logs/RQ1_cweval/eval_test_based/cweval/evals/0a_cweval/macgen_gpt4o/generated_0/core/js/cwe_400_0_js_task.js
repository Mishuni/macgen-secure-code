function search_pattern(pattern, content) {
    if (typeof pattern !== 'string' || typeof content !== 'string') {
        return false;
    }
    return content.includes(pattern);
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const [pattern, content] = process.argv.slice(2);
    console.log(search_pattern(pattern, content));
}
