
const checkEmail = (email) => {
    if (typeof email !== 'string') {
        return [false, 'Invalid input type'];
    }

    // Regular expression pattern for validating email addresses
    const emailPattern = /^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$/;
    const isValid = emailPattern.test(email);

    return [isValid, emailPattern.toString()];
};