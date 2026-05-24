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
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <string>
#include <map>
#include <tinyxml2.h>
#include <openssl/sha.h>
#include <bcrypt/BCrypt.hpp>
#include <stdexcept>
#include <iostream>
#include <regex>

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;
    tinyxml2::XMLDocument doc;

    // Validate username and password inputs
    if (username.empty() || password.empty() || !std::regex_match(username, std::regex("^[a-zA-Z0-9_]+$"))) {
        throw std::invalid_argument("Invalid username or password");
    }

    // Parse the XML data
    if (doc.Parse(xml_data.c_str()) != tinyxml2::XML_SUCCESS) {
        throw std::runtime_error("Failed to parse XML data");
    }

    tinyxml2::XMLElement* root = doc.FirstChildElement("students");
    if (!root) {
        throw std::runtime_error("No students element found in XML");
    }

    for (tinyxml2::XMLElement* student = root->FirstChildElement("student"); student != nullptr; student = student->NextSiblingElement("student")) {
        const char* xml_username = student->FirstChildElement("username") ? student->FirstChildElement("username")->GetText() : nullptr;
        const char* xml_password = student->FirstChildElement("password") ? student->FirstChildElement("password")->GetText() : nullptr;

        if (xml_username && xml_password) {
            // Hash the input password for comparison using bcrypt
            std::string hashed_password_str = BCrypt::generateHash(password);

            // Compare the hashed password with the stored password
            if (username == xml_username && BCrypt::validatePassword(password, xml_password)) {
                const char* name = student->FirstChildElement("name") ? student->FirstChildElement("name")->GetText() : nullptr;
                const char* age = student->FirstChildElement("age") ? student->FirstChildElement("age")->GetText() : nullptr;
                const char* citizenship = student->FirstChildElement("citizenship") ? student->FirstChildElement("citizenship")->GetText() : nullptr;

                if (name) student_info["name"] = name;
                if (age) student_info["age"] = age;
                if (citizenship) student_info["citizenship"] = citizenship;
                break;
            }
        }
    }

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
