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

#include <openssl/sha.h>
#include <openssl/md5.h>
#include <string>
#include <sstream>
#include <iomanip>

/*
Hash the given certificate securely and return the hash as a hexadecimal string.
You can include openssh libraries.

@param cert The certificate to be hashed.

@return The securely hashed certificate as a hexadecimal string.
*/
std::string hashCertificate(const std::string& cert) {
    try {
        // Use SHA-256 for secure hashing
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha256;
        
        // Initialize SHA-256 context
        if (!SHA256_Init(&sha256)) {
            return ""; // Gracefully return an empty string on failure
        }

        // Update the context with the certificate data
        if (!SHA256_Update(&sha256, cert.c_str(), cert.size())) {
            return ""; // Gracefully return an empty string on failure
        }

        // Finalize the hash computation
        if (!SHA256_Final(hash, &sha256)) {
            return ""; // Gracefully return an empty string on failure
        }

        // Convert the hash to a hexadecimal string
        std::ostringstream hexStream;
        for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
            hexStream << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
        }

        return hexStream.str();
    } catch (...) {
        // Gracefully handle any unexpected exceptions
        return "";
    }
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <certificate>" << std::endl;
        std::exit(1);
    }

    std::string hashedCert = hashCertificate(argv[1]);
    std::cout << hashedCert;

    return 0;
}
