
#include <iostream>
#include <fstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <stdexcept>
#include <filesystem>
#include <openssl/evp.h>
#include <openssl/rand.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Validate inputs
    if (directory.empty() || filename.empty()) {
        throw std::invalid_argument("Directory and filename must not be empty.");
    }

    // Check if the directory exists and is writable
    if (!std::filesystem::exists(directory) || !std::filesystem::is_directory(directory)) {
        throw std::runtime_error("Directory does not exist: " + directory);
    }

    std::error_code ec;
    auto perms = std::filesystem::status(directory, ec).permissions();
    if (ec || !(perms & std::filesystem::perms::owner_write)) {
        throw std::runtime_error("Directory is not writable: " + directory);
    }

    // Create the full path for the file
    std::filesystem::path fullPath = std::filesystem::path(directory) / filename;

    // Check for directory traversal attack
    if (fullPath.has_parent_path() && fullPath.parent_path() != std::filesystem::path(directory)) {
        throw std::invalid_argument("Invalid file path.");
    }

    // Open the file for writing
    std::ofstream outFile(fullPath, std::ios::binary);
    if (!outFile) {
        throw std::runtime_error("Unable to open file for writing: " + fullPath.string());
    }

    // Encrypt the content
    std::string encryptedContent;
    unsigned char key[32]; // 256-bit key
    unsigned char iv[16];  // 128-bit IV

    // Generate a random key and IV
    if (!RAND_bytes(key, sizeof(key)) || !RAND_bytes(iv, sizeof(iv))) {
        throw std::runtime_error("Failed to generate random key or IV.");
    }

    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create cipher context.");
    }

    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), nullptr, key, iv) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to initialize encryption.");
    }

    unsigned char buffer[1024];
    int outLen;
    if (EVP_EncryptUpdate(ctx, buffer, &outLen, reinterpret_cast<const unsigned char*>(content.data()), content.size()) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Encryption failed during update.");
    }
    encryptedContent.append(reinterpret_cast<char*>(buffer), outLen);

    if (EVP_EncryptFinal_ex(ctx, buffer, &outLen) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Encryption failed during finalization.");
    }
    encryptedContent.append(reinterpret_cast<char*>(buffer), outLen);
    EVP_CIPHER_CTX_free(ctx);

    // Write the encrypted content to the file
    outFile.write(encryptedContent.c_str(), encryptedContent.size());
    outFile.close();

    // Set the file permissions to be accessible only by the current user
    if (chmod(fullPath.c_str(), S_IRUSR | S_IWUSR) != 0) {
        throw std::runtime_error("Unable to set file permissions: " + fullPath.string());
    }
}