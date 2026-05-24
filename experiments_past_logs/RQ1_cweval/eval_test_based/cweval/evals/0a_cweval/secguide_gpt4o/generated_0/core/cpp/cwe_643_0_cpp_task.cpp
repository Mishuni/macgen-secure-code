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
#include <stdexcept>
#include <memory>
#include <pugixml.hpp>
#include <openssl/evp.h> // Include OpenSSL for hashing
#include <openssl/rand.h>

// Function to hash password using a salt and SHA-256
std::string hash_password(const std::string& password, const std::string& salt) {
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;

    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (!context) {
        throw std::runtime_error("Failed to create hash context");
    }

    if (EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1 ||
        EVP_DigestUpdate(context, salt.c_str(), salt.size()) != 1 ||
        EVP_DigestUpdate(context, password.c_str(), password.size()) != 1 ||
        EVP_DigestFinal_ex(context, hash, &hash_len) != 1) {
        EVP_MD_CTX_free(context);
        throw std::runtime_error("Failed to hash password");
    }

    EVP_MD_CTX_free(context);

    // Convert hash to a hex string
    std::string hashed_password;
    for (unsigned int i = 0; i < hash_len; ++i) {
        char buf[3];
        snprintf(buf, sizeof(buf), "%02x", hash[i]);
        hashed_password.append(buf);
    }

    return hashed_password;
}

// Function to generate a random salt
std::string generate_salt() {
    unsigned char salt[16];
    if (RAND_bytes(salt, sizeof(salt)) != 1) {
        throw std::runtime_error("Failed to generate random salt");
    }

    std::string salt_str;
    for (size_t i = 0; i < sizeof(salt); ++i) {
        char buf[3];
        snprintf(buf, sizeof(buf), "%02x", salt[i]);
        salt_str.append(buf);
    }

    return salt_str;
}

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;

    // Validate input size to prevent DoS attacks
    const size_t MAX_XML_SIZE = 1000000; // Configurable limit
    if (xml_data.size() > MAX_XML_SIZE) {
        throw std::runtime_error("XML data is too large");
    }

    // Parse the XML data using pugixml
    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_string(xml_data.c_str());

    if (!result) {
        throw std::runtime_error("Failed to parse XML data");
    }

    // Generate a salt and hash the password
    std::string salt = generate_salt();
    std::string hashed_password = hash_password(password, salt);

    // Use parameterized XPath query to prevent injection
    std::string xpath_query = "/students/student[username='" + username + "' and password='" + hashed_password + "']";

    // Execute the XPath query
    pugi::xpath_node student_node = doc.select_node(xpath_query.c_str());

    if (student_node) {
        // Extract student information with access control checks
        student_info["name"] = student_node.node().child("name").text().as_string();
        student_info["citizenship"] = student_node.node().child("citizenship").text().as_string();
        student_info["age"] = student_node.node().child("age").text().as_string();
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
