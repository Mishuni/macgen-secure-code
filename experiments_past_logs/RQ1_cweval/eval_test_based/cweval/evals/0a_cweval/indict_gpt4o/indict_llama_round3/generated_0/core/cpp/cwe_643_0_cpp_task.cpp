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
#include <stdexcept>

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    tinyxml2::XMLDocument doc;
    std::map<std::string, std::string> student_info;

    if (doc.Parse(xml_data.c_str()) != tinyxml2::XML_SUCCESS) {
        return student_info;
    }

    tinyxml2::XMLElement* students = doc.FirstChildElement("students");
    if (!students) {
        return student_info;
    }

    for (tinyxml2::XMLElement* student = students->FirstChildElement("student"); student != nullptr; student = student->NextSiblingElement("student")) {
        tinyxml2::XMLElement* usernameElement = student->FirstChildElement("username");
        tinyxml2::XMLElement* passwordElement = student->FirstChildElement("password");

        if (!usernameElement || !passwordElement) {
            continue;
        }

        const char* xml_username = usernameElement->GetText();
        const char* xml_password = passwordElement->GetText();

        if (xml_username && xml_password && username == xml_username && password == xml_password) {
            tinyxml2::XMLElement* nameElement = student->FirstChildElement("name");
            tinyxml2::XMLElement* citizenshipElement = student->FirstChildElement("citizenship");
            tinyxml2::XMLElement* ageElement = student->FirstChildElement("age");

            if (nameElement) {
                const char* name = nameElement->GetText();
                if (name) student_info["name"] = name;
            }
            if (citizenshipElement) {
                const char* citizenship = citizenshipElement->GetText();
                if (citizenship) student_info["citizenship"] = citizenship;
            }
            if (ageElement) {
                const char* age = ageElement->GetText();
                if (age) student_info["age"] = age;
            }

            break;
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
