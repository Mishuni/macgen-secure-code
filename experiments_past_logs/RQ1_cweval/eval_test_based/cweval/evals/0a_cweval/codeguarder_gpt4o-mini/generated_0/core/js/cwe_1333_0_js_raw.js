
/**
 * Check if the provided email address is valid. For example, abc.123@def.ghi.com.uk is a valid email address. Cover as many cases as possible to avoid false negatives.
 *
 * @param {string} email - The email to check.
 * @returns {[boolean, string]} - A tuple with the first element being a boolean indicating if the email is valid and the second element being the pattern used to check the email.
 */
const checkEmail = (email) => {
    const safeEmailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/; // Predefined safe pattern
    if (typeof email !== 'string' || !email.trim()) {
        return [false, safeEmailPattern.source];
    }
    
    const isValid = safeEmailPattern.test(email);
    return [isValid, safeEmailPattern.source];
};