const { JSDOM } = require('jsdom');
const xpath = require('xpath');

function getStudentInfo(xml_data, username, password) {
    // Validate inputs to ensure they are alphanumeric
    const validInput = /^[a-zA-Z0-9_]+$/;
    if (!validInput.test(username) || !validInput.test(password)) {
        return null;
    }

    // Function to escape special characters for XPath
    const escapeForXPath = (str) => str.replace(/'/g, "&apos;").replace(/"/g, "&quot;");

    const dom = new JSDOM(xml_data, { contentType: "application/xml" });
    const doc = dom.window.document;

    // Construct the XPath query with escaped inputs
    const query = `/students/student[username/text()='${escapeForXPath(username)}' and password/text()='${escapeForXPath(password)}']`;
    const studentNode = xpath.select1(query, doc);

    if (studentNode) {
        const name = xpath.select1('string(./name)', studentNode);
        const age = xpath.select1('string(./age)', studentNode);
        const citizenship = xpath.select1('string(./citizenship)', studentNode);

        return {
            name: name,
            age: age,
            citizenship: citizenship
        };
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
