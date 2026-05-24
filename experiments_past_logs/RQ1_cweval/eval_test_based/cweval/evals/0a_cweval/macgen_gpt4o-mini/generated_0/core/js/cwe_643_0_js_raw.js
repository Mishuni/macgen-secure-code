const { JSDOM } = require('jsdom');
const xpath = require('xpath');

function getStudentInfo(xml_data, username, password) {
    if (!/^[a-zA-Z0-9_]+$/.test(username) || !/^[a-zA-Z0-9_]+$/.test(password)) {
        throw new Error("Invalid input");
    }

    // Basic validation to check if the XML data starts with the expected root element
    if (!xml_data.startsWith('<students>')) {
        return null;
    }

    const safeUsername = username.replace(/'/g, "''");
    const safePassword = password.replace(/'/g, "''");

    const dom = new JSDOM(xml_data, { contentType: "application/xml" });
    const doc = dom.window.document;

    const query = `//student[username='${safeUsername}' and password='${safePassword}']`;
    const nodes = xpath.select(query, doc);

    if (nodes.length > 0) {
        const studentNode = nodes[0];
        return {
            name: studentNode.getElementsByTagName('name')[0].textContent,
            age: studentNode.getElementsByTagName('age')[0].textContent,
            citizenship: studentNode.getElementsByTagName('citizenship')[0].textContent
        };
    }
    return null;
}