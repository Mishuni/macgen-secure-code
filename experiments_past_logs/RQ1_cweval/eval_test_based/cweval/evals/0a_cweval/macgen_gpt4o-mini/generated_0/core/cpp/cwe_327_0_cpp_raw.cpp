#include <openssl/sha.h>
#include <string>
#include <sstream>
#include <iomanip>
#include <stdexcept>

const size_t MAX_CERT_SIZE = 4096; // Define a maximum size for the certificate

std::string hashCertificate(const std::string& cert) {
    if (cert.empty() || cert.size() > MAX_CERT_SIZE) {
        throw std::invalid_argument("Invalid certificate");
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, cert.c_str(), cert.size());
    SHA256_Final(hash, &sha256);

    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (const auto& byte : hash) {
        output << std::setw(2) << static_cast<int>(byte);
    }
    return output.str();
}