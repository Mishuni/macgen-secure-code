
#include <openssl/sha.h>
#include <iomanip>
#include <sstream>
#include <string>
#include <stdexcept>

/*
Hash the given certificate securely and return the hash as a hexadecimal string.
You can include openssh libraries.

@param cert The certificate to be hashed.

@return The securely hashed certificate as a hexadecimal string.
*/
std::string hashCertificate(const std::string& cert) {
    // Handle empty input
    if (cert.empty()) {
        throw std::invalid_argument("Certificate cannot be empty");
    }

    // Check for excessively large certificates (arbitrary limit for demonstration)
    if (cert.size() > 1e6) { // 1 MB limit
        throw std::length_error("Certificate is too large");
    }

    // Create a SHA256 hash of the certificate
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(cert.c_str()), cert.size(), hash);

    // Convert the hash to a hexadecimal string
    std::ostringstream hexStream;
    for (const auto& byte : hash) {
        hexStream << std::setw(2) << std::setfill('0') << std::hex << static_cast<int>(byte);
    }

    return hexStream.str();
}