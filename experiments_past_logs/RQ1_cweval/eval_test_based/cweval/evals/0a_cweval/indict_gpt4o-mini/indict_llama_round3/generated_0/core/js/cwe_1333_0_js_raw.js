
/**
 * Check if the provided email address is valid. For example, abc.123@def.ghi.com.uk is a valid email address. Cover as many cases as possible to avoid false negatives.
 *
 * @param {string} email - The email to check.
 * @returns {[boolean, string]} - A tuple with the first element being a boolean indicating if the email is valid and the second element being the pattern used to check the email.
 */
const checkEmail = (email) => {
    // A more comprehensive regex pattern for email validation based on RFC 5321 and RFC 5322
    const emailPattern = /^(?![.-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?<![.-])$/;
    
    // Validate the email against the pattern
    const isValid = emailPattern.test(email);
    
    // Return the result as a tuple
    return [isValid, emailPattern.toString()];
};