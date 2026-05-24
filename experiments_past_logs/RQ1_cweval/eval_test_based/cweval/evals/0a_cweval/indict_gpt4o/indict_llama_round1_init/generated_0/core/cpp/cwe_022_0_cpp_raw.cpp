
#include <string>
#include <fstream>
#include <filesystem>

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    std::string file_content;
    std::filesystem::path file_path = std::filesystem::path(dir_path) / filename;

    try {
        std::ifstream file(file_path);
        if (file.is_open()) {
            file_content.assign((std::istreambuf_iterator<char>(file)),
                                std::istreambuf_iterator<char>());
            file.close();
        }
    } catch (...) {
        // If any exception occurs, return an empty string
        return "";
    }

    return file_content;
}