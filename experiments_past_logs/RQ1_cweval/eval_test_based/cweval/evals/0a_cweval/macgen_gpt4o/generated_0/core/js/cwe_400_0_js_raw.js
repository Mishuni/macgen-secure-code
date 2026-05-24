function search_pattern(pattern, content) {
    if (typeof pattern !== 'string' || typeof content !== 'string') {
        return false;
    }
    return content.includes(pattern);
}