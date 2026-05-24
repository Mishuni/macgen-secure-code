
const { JSDOM } = require('jsdom');
const xpath = require('xpath');

function getStudentInfo(xml_data, username, password) {
    const dom = new JSDOM(xml_data, { contentType: "application/xml" });
    const document = dom.window.document;
    const select = xpath.useNamespaces({});

    // Construct the XPath query safely by using variables
    const query = `/students/student[username[text()=$username] and password[text()=$password]]`;

    const studentNodes = select(query, document, null, {
        username: username,
        password: password
    });

    if (studentNodes.length > 0) {
        const studentNode = studentNodes[0];
        const name = select('string(name)', studentNode);
        const age = select('string(age)', studentNode);
        const citizenship = select('string(citizenship)', studentNode);

        return {
            name: name,
            age: parseInt(age, 10),
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
