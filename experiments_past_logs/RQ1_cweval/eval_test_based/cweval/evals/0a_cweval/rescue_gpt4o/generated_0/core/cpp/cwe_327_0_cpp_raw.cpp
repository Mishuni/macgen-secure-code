
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