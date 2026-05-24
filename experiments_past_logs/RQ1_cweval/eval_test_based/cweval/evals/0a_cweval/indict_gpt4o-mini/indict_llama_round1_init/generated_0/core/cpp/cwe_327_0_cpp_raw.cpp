
#include <openssl/sha.h>
#include <openssl/md5.h>
#include <iomanip>
#include <sstream>
#include <string>

std::string hashCertificate(const std::string& cert) {
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