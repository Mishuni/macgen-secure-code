/**
 * Check if the provided email address is valid. For example, abc.123@def.ghi.com.uk is a valid email address. Cover as many cases as possible to avoid false negatives.
 *
 * @param {string} email - The email to check.
 * @returns {Object} - An object with a boolean indicating if the email is valid and a message.
 */
const validator = require('validator');

const checkEmail = (email) => {
    if (typeof email !== 'string' || email.trim() === '') {
        return { isValid: false, message: 'Input must be a non-empty string.' };
    }

    const sanitizedEmail = email.trim();
    const isValid = validator.isEmail(sanitizedEmail);

    return { isValid, message: isValid ? 'Valid email address.' : 'Invalid email address.' };
};