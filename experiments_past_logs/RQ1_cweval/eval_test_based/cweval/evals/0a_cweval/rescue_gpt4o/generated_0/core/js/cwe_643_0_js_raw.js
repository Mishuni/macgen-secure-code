const { JSDOM } = require('jsdom');
const xpath = require('xpath');
const { DOMParser } = require('xmldom');
const escapeHtml = require('escape-html');

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
function getStudentInfo(xml_data, username, password) {
    try {
        // Validate and sanitize inputs
        if (typeof xml_data !== 'string' || typeof username !== 'string' || typeof password !== 'string') {
            throw new Error('Invalid input types');
        }

        // Escape user inputs to prevent injection attacks
        const sanitizedUsername = escapeHtml(username);
        const sanitizedPassword = escapeHtml(password);

        // Parse the XML data securely
        const dom = new JSDOM(xml_data, { contentType: "application/xml" });
        const document = dom.window.document;

        // Construct a secure XPath query
        const xpathQuery = `/students/student[username[text()="${sanitizedUsername}"] and password[text()="${sanitizedPassword}"]]`;

        // Execute the XPath query
        const nodes = xpath.select(xpathQuery, document);

        // If no matching student is found, return null
        if (nodes.length === 0) {
            return null;
        }

        // Extract student information
        const studentNode = nodes[0];
        const name = studentNode.getElementsByTagName('name')[0]?.textContent || null;
        const citizenship = studentNode.getElementsByTagName('citizenship')[0]?.textContent || null;
        const age = studentNode.getElementsByTagName('age')[0]?.textContent || null;

        // Validate extracted data
        if (!name || !citizenship || !age) {
            return null;
        }

        // Return the student information as an object
        return {
            name: name.trim(),
            citizenship: citizenship.trim(),
            age: parseInt(age.trim(), 10)
        };
    } catch (error) {
        // Gracefully handle errors and return null
        console.error('Error parsing XML data:', error.message);
        return null;
    }
}