
#include <iostream>
#include <map>
#include <string>
#include <tinyxml2.h>
#include <algorithm>
#include <cctype>
#include <openssl/sha.h>
#include <iomanip>
#include <sstream>
#include <stdexcept>

std::string hash_password(const std::string& password) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(password.c_str()), password.size(), hash);
    
    std::ostringstream oss;
    for (const auto& byte : hash) {
        oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
    }
    return oss.str();
}

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;

    tinyxml2::XMLDocument doc;
    if (doc.Parse(xml_data.c_str()) != tinyxml2::XML_SUCCESS) {
        throw std::runtime_error("Failed to parse XML data"); // Improved error handling
    }

    tinyxml2::XMLElement* root = doc.FirstChildElement("students");
    if (!root) {
        throw std::runtime_error("Root element 'students' not found"); // Improved error handling
    }

    std::string hashed_password = hash_password(password);

    for (tinyxml2::XMLElement* student = root->FirstChildElement("student"); student != nullptr; student = student->NextSiblingElement("student")) {
        const char* user = student->FirstChildElement("username")->GetText();
        const char* pass = student->FirstChildElement("password")->GetText();
        
        // Ensure case-insensitive comparison for username
        if (user && pass && 
            strcasecmp(username.c_str(), user) == 0 && 
            hashed_password == pass) {
            const char* name = student->FirstChildElement("name")->GetText();
            const char* citizenship = student->FirstChildElement("citizenship")->GetText();
            const char* age = student->FirstChildElement("age")->GetText();

            if (name) student_info["name"] = name;
            if (citizenship) student_info["citizenship"] = citizenship;
            if (age) student_info["age"] = age;

            break; // Exit loop after finding the matching student
        }
    }

    return student_info; // Return the found student info or empty map if not found
}