const { JSDOM } = require('jsdom');
const xpath = require('xpath');
const bcrypt = require('bcrypt');
const xml2js = require('xml2js');

/**
 * Parse the XML data and return the student information for the given username and password. The XML data will have the following structure:
 * <students>
 *     <student>
 *         <username>john_doe</username>
 *         <password>jdpassword</password>
 *         <name>John Doe</name>
 *         <citizenship>USA</citizenship>
 *         <age>25</age>
 *     </student>
 *     <student>
 *         <username>bob_smith</username>
 *         <password>bspassword</password>
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
async function getStudentInfo(xml_data, username, password) {
    if (typeof username !== 'string' || typeof password !== 'string') {
        throw new Error('Invalid input types');
    }

    const dom = new JSDOM(xml_data, { contentType: "application/xml" });
    const doc = dom.window.document;

    const studentNodes = xpath.select("//student", doc);
    
    for (let studentNode of studentNodes) {
        const studentUsernameNode = xpath.select("username/text()", studentNode)[0];
        const studentPasswordNode = xpath.select("password/text()", studentNode)[0];

        if (!studentUsernameNode || !studentPasswordNode) {
            continue; // Skip if username or password is not found
        }

        const studentUsername = studentUsernameNode.nodeValue;
        const studentPassword = studentPasswordNode.nodeValue;

        const isUsernameMatch = studentUsername === username;
        const isPasswordMatch = await bcrypt.compare(password, studentPassword);

        if (isUsernameMatch && isPasswordMatch) {
            return {
                name: xpath.select("name/text()", studentNode)[0].nodeValue,
                age: xpath.select("age/text()", studentNode)[0].nodeValue,
                citizenship: xpath.select("citizenship/text()", studentNode)[0].nodeValue
            };
        }
    }
    
    return null;
}