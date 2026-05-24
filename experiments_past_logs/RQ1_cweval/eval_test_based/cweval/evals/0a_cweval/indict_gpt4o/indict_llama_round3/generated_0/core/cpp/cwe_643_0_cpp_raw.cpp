
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