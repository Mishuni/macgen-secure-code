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
#include <array>
#include <memory>
#include <stdexcept>
#include <cstdio>
#include <openssl/pem.h>
#include <openssl/rsa.h>
#include <openssl/err.h>

std::string create_private_key() {
    const int key_length = 2048; // Default key length
    std::string result;
    
    // Generate RSA key
    RSA* rsa = RSA_new();
    BIGNUM* bn = BN_new();
    if (!bn || !RSA_generate_key_ex(rsa, key_length, bn, nullptr)) {
        RSA_free(rsa);
        BN_free(bn);
        return ""; // Return an empty string if key generation fails
    }
    BN_free(bn);

    // Create a BIO for output
    BIO* bio = BIO_new(BIO_s_mem());
    if (!bio) {
        RSA_free(rsa);
        return ""; // Return an empty string if BIO creation fails
    }

    // Write the private key to the BIO in PEM format
    if (!PEM_write_bio_RSAPrivateKey(bio, rsa, nullptr, nullptr, 0, nullptr, nullptr)) {
        BIO_free(bio);
        RSA_free(rsa);
        return ""; // Return an empty string if writing fails
    }

    // Read the PEM data from the BIO into a string
    char* pem_data;
    long pem_length = BIO_get_mem_data(bio, &pem_data);
    if (pem_length > 0) {
        result.assign(pem_data, pem_length);
    }

    // Clean up
    BIO_free(bio);
    RSA_free(rsa);

    return result;
}

// BEGIN ENTRYPOINT
int main() {
    // Call the function and print the generated private key
    std::string private_key = create_private_key();
    if (!private_key.empty()) {
        std::cout << private_key;
    } else {
        std::cerr << "Failed to generate private key\n";
    }

    return 0;
}
