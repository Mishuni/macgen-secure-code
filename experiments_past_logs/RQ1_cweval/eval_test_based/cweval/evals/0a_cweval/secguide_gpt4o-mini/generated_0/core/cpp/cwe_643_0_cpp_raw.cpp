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