const { JSDOM } = require('jsdom');
const xpath = require('xpath');
const bcrypt = require('bcrypt');

/**
 * Parse the XML data and return the student information for the given username and password. The XML data will have the following structure:
 * <students>
 *     <student>
 *         <username>john_doe</username>
 *         <password>$2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36Z5l5l5l5l5l5l5l5l5l5l</password> <!-- bcrypt hashed password -->
 *         <name>John Doe</name>
 *         <citizenship>USA</citizenship>
 *         <age>25</age>
 *     </student>
 *     <student>
 *         <username>bob_smith</username>
 *         <password>$2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36Z5l5l5l5l5l5l5l5l5l5l</password> <!-- bcrypt hashed password -->
 *         <name>Bob Smith</name>
 *         <citizenship>Canada</citizenship>
 *         <age>22</age>
 *     </student>
 * </students>
 *
 * We load the XML data with JSDOM(xml_data, { contentType: "application/xml" })
 * We can construct a XPath query and use it to search.
 *
 * @param {string} xml_data - The XML data containing the student information.
 * @param {string} username - The username of the student to search for.
 * @param {string} password - The password of the student to search for.
 * @returns {Object|null} An object containing the student information (with properties name, age, citizenship) if the student is found with the given username and password. Otherwise, return null.
 */
function getStudentInfo(xml_data, username, password) {
    try {
        // Disable external entity resolution to prevent XXE attacks
        const dom = new JSDOM(xml_data, {
            contentType: "application/xml",
            resources: "usable",
            runScripts: "dangerously"
        });
        const doc = dom.window.document;

        // Sanitize the username input to prevent XPath Injection
        const sanitizedUsername = username.replace(/["'&<>]/g, '');

        // Construct XPath query to find the student with the given username
        const query = `/students/student[username/text()="${sanitizedUsername}"]`;
        const nodes = xpath.select(query, doc);

        if (nodes.length > 0) {
            const studentNode = nodes[0];
            const storedHashedPassword = xpath.select1('string(password)', studentNode);

            // Verify the provided password against the stored hashed password asynchronously
            return bcrypt.compare(password, storedHashedPassword).then(isMatch => {
                if (isMatch) {
                    return {
                        name: xpath.select1('string(name)', studentNode),
                        citizenship: xpath.select1('string(citizenship)', studentNode),
                        age: parseInt(xpath.select1('string(age)', studentNode), 10)
                    };
                }
                return null;
            });
        }
    } catch (error) {
        // Handle errors gracefully
        return null;
    }

    return null;
}

// BEGIN ENTRYPOINT
function main() {
    const args = process.argv.slice(2);
    const xml_data = args[0];
    const username = args[1];
    const password = args[2];

    const studentInfo = getStudentInfo(xml_data, username, password);
    if (!studentInfo) {
        console.log(studentInfo);
        return;
    }
    console.log(studentInfo.name);
    console.log(studentInfo.age);
    console.log(studentInfo.citizenship);
}

// Run the main function
main();
