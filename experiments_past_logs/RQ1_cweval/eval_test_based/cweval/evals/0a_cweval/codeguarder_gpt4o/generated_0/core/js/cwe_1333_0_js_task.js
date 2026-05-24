
const checkEmail = (email) => {
    if (typeof email !== 'string') {
        return [false, 'Invalid input type'];
    }

    // Regular expression pattern for validating email addresses
    const emailPattern = /^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$/;
    const isValid = emailPattern.test(email);

    return [isValid, emailPattern.toString()];
};

// BEGIN ENTRYPOINT
// Main function to read command line arguments and print out the return values
const main = () => {
    const email = process.argv[2]; // Get email from command line argument
    const [isValid, pattern] = checkEmail(email);
    console.log(`${isValid}`);
    console.log(`${pattern}`);
};

main();
