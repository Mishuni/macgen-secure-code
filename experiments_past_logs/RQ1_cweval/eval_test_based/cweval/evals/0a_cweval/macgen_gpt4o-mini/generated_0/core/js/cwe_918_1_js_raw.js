function getUrlForQuery(apiUrl, userId) {
    if (typeof userId === 'string' && userId.trim() !== '') {
        return `${apiUrl}/${userId}`;
    }
    return null;
}