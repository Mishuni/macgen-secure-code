function getUrlForQuery(apiUrl, userId) {
    if (!userId || typeof userId !== 'string' || !/^[a-zA-Z0-9]+$/.test(userId)) {
        return null;
    }
    
    try {
        new URL(apiUrl);
    } catch (e) {
        return null;
    }

    const encodedUserId = encodeURIComponent(userId);
    
    if (!apiUrl.endsWith('/')) {
        apiUrl += '/';
    }
    
    return apiUrl + encodedUserId;
}