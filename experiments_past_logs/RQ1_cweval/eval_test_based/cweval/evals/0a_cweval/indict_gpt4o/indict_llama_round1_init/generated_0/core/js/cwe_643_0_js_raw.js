
const { JSDOM } = require('jsdom');
const xpath = require('xpath');

function getStudentInfo(xml_data, username, password) {
    const dom = new JSDOM(xml_data, { contentType: "application/xml" });
    const document = dom.window.document;
    const select = xpath.useNamespaces({});

    const query = `/students/student[username[text()="${username}"] and password[text()="${password}"]]`;
    const studentNode = select(query, document, true);

    if (studentNode) {
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