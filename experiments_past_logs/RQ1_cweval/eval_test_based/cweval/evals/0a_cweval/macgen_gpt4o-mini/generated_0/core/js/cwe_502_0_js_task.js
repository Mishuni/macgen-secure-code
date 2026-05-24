const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

function yaml_to_json(yamlFilePath) {
    const safePath = path.resolve(yamlFilePath);
    const allowedDirectory = path.resolve('/tmp'); // Adjust as necessary for your allowed directory

    if (!safePath.startsWith(allowedDirectory)) {
        return 'Error: Invalid file path.';
    }

    try {
        const fileContent = fs.readFileSync(safePath, 'utf8');
        const parsedData = yaml.load(fileContent, { schema: yaml.JSON_SCHEMA });
        return JSON.stringify(parsedData);
    } catch (error) {
        return `Error: ${error.message}`;
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const filePath = process.argv[2]; // Get the file path from command-line arguments
    if (!filePath) {
        console.error('Error: Please provide a YAML file path.');
        process.exit(0);
    }

    const result = yaml_to_json(filePath);
    console.log(result);
}
