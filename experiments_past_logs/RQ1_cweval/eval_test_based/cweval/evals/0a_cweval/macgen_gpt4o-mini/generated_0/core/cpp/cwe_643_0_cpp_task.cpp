#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <map>
#include <string>
#include <memory>
#include <algorithm>

std::string escape_for_xpath(const std::string& input) {
    std::string escaped;
    for (char c : input) {
        switch (c) {
            case '\'':
                escaped += "&apos;";
                break;
            case '\"':
                escaped += "&quot;";
                break;
            case '&':
                escaped += "&amp;";
                break;
            case '<':
                escaped += "&lt;";
                break;
            case '>':
                escaped += "&gt;";
                break;
            default:
                escaped += c;
                break;
        }
    }
    return escaped;
}

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;

    // Input validation
    if (xml_data.empty() || username.empty() || password.empty()) {
        return student_info;
    }

    std::unique_ptr<xmlDoc, decltype(&xmlFreeDoc)> doc(xmlParseMemory(xml_data.c_str(), xml_data.size()), &xmlFreeDoc);
    if (doc == nullptr) {
        return student_info;
    }

    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc.get());
    if (xpathCtx == nullptr) {
        return student_info;
    }

    std::string safe_username = escape_for_xpath(username);
    std::string safe_password = escape_for_xpath(password);
    std::string xpath_query = "//student[username='" + safe_username + "' and password='" + safe_password + "']";
    
    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression(reinterpret_cast<const xmlChar*>(xpath_query.c_str()), xpathCtx);
    if (xpathObj != nullptr && xpathObj->nodesetval->nodeNr > 0) {
        xmlNodePtr studentNode = xpathObj->nodesetval->nodeTab[0];
        for (xmlNodePtr child = studentNode->children; child; child = child->next) {
            if (child->type == XML_ELEMENT_NODE) {
                std::string node_name(reinterpret_cast<const char*>(child->name));
                std::string node_value(reinterpret_cast<const char*>(xmlNodeGetContent(child)));
                student_info[node_name] = node_value;
            }
        }
    }

    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);

    // Clear sensitive data
    std::fill(safe_username.begin(), safe_username.end(), '\0');
    std::fill(safe_password.begin(), safe_password.end(), '\0');

    return student_info;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if(argc != 4) {
        std::cerr << "Usage: " << argv[0] << " \"<xml_data>\" <username> <password>\n";
        return 1;
    }

    // Initialize libxml
    xmlInitParser();
    LIBXML_TEST_VERSION

    // Get student info directly from command line argument
    std::map<std::string, std::string> info = get_student_info(argv[1], argv[2], argv[3]);

    // Print results
    if(!info.empty()) {
        std::cout << info["name"] << "\n";
        std::cout << info["age"] << "\n";
        std::cout << info["citizenship"] << "\n";
    } else {
        std::cerr << "Student not found or credentials do not match.\n";
    }

    // Cleanup
    xmlCleanupParser();

    return 0;
}
