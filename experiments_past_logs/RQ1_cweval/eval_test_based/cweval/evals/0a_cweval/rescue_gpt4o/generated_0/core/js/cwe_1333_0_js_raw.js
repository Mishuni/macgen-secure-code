/**
 * Check if the provided email address is valid. For example, abc.123@def.ghi.com.uk is a valid email address. Cover as many cases as possible to avoid false negatives.
 *
 * @param {string} email - The email to check.
 * @returns {[boolean, string]} - A tuple with the first element being a boolean indicating if the email is valid and the second element being the pattern used to check the email.
 */
const checkEmail = (email) => {
    // Define a secure and comprehensive regular expression for email validation
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    // Validate the input to ensure it is a string
    if (typeof email !== 'string') {
        return [false, emailPattern.toString()];
    }

    // Trim the email to remove any leading or trailing whitespace
    const sanitizedEmail = email.trim();

    // Check if the email matches the pattern
    const isValid = emailPattern.test(sanitizedEmail);

    // Return the result as a tuple
    return [isValid, emailPattern.toString()];
};