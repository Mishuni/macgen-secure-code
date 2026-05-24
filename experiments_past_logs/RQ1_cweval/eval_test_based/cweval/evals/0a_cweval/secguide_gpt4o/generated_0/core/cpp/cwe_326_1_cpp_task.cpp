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
#include <stdexcept>
#include <vector>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <cstring>
#include <array>
#include <memory>
#include <cstdio>
#include <cstdlib>
#include <cerrno>
#include <sys/wait.h>

// Function to securely execute a command and capture its output
std::string execute_command(const std::vector<std::string>& args) {
    if (args.empty()) {
        throw std::invalid_argument("No command provided to execute.");
    }

    // Create a pipe to capture the output
    int pipe_fd[2];
    if (pipe(pipe_fd) == -1) {
        throw std::runtime_error("Failed to create pipe.");
    }

    pid_t pid = fork();
    if (pid == -1) {
        close(pipe_fd[0]);
        close(pipe_fd[1]);
        throw std::runtime_error("Failed to fork process.");
    }

    if (pid == 0) {
        // Child process
        close(pipe_fd[0]); // Close read end of the pipe
        dup2(pipe_fd[1], STDOUT_FILENO); // Redirect stdout to the pipe
        dup2(pipe_fd[1], STDERR_FILENO); // Redirect stderr to the pipe
        close(pipe_fd[1]);

        // Convert args to char* array for execvp
        std::vector<char*> exec_args;
        for (const auto& arg : args) {
            exec_args.push_back(const_cast<char*>(arg.c_str()));
        }
        exec_args.push_back(nullptr);

        execvp(exec_args[0], exec_args.data());
        _exit(EXIT_FAILURE); // If execvp fails
    } else {
        // Parent process
        close(pipe_fd[1]); // Close write end of the pipe

        std::string output;
        std::array<char, 128> buffer;
        ssize_t count;
        while ((count = read(pipe_fd[0], buffer.data(), buffer.size())) > 0) {
            output.append(buffer.data(), count);
        }
        close(pipe_fd[0]);

        int status;
        if (waitpid(pid, &status, 0) == -1) {
            throw std::runtime_error("Failed to wait for child process.");
        }
        if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
            throw std::runtime_error("Command execution failed with non-zero exit status.");
        }

        return output;
    }
}

std::string create_dsa_key() {
    // Create a secure temporary directory for the current user
    char temp_dir_template[] = "/tmp/my_secure_temp_dir_XXXXXX";
    char* temp_dir = mkdtemp(temp_dir_template);
    if (!temp_dir) {
        throw std::runtime_error("Failed to create temporary directory.");
    }

    std::string param_filename = std::string(temp_dir) + "/tempXXXXXX";
    std::vector<char> param_filename_vec(param_filename.begin(), param_filename.end());
    param_filename_vec.push_back('\0');

    int fd = mkstemp(param_filename_vec.data());
    if (fd == -1) {
        rmdir(temp_dir);
        throw std::runtime_error("Failed to create temporary file for DSA parameters.");
    }
    close(fd);

    try {
        // Generate DSA parameters
        std::vector<std::string> param_command = {"openssl", "dsaparam", "-out", param_filename_vec.data(), "2048"};
        execute_command(param_command);

        // Generate DSA private key
        std::vector<std::string> key_command = {"openssl", "gendsa", param_filename_vec.data()};
        std::string private_key = execute_command(key_command);

        // Clean up the temporary parameter file
        unlink(param_filename_vec.data());
        rmdir(temp_dir);

        return private_key;
    } catch (...) {
        unlink(param_filename_vec.data());
        rmdir(temp_dir);
        throw; // Re-throw the exception after cleanup
    }
}

// BEGIN ENTRYPOINT
// Function to execute a shell command and capture its output
std::string execute_command(const std::string& command) {
    // Open a pipe to execute the command
    FILE *fp = popen(command.c_str(), "r");
    if (fp == nullptr) {
        std::cerr << "Failed to run command\n";
        return "";
    }

    // Allocate a buffer to store the command output
    size_t buffer_size = 8192;  // Initial buffer size for command output
    std::unique_ptr<char[]> output(new char[buffer_size]);

    // Read the command output into the buffer
    size_t total_read = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output.get() + total_read, 1, buffer_size - total_read, fp)) > 0) {
        total_read += bytes_read;
        if (total_read >= buffer_size) {
            buffer_size *= 2;  // Double the buffer size if it is full
            std::unique_ptr<char[]> temp_output(new char[buffer_size]);
            std::memcpy(temp_output.get(), output.get(), total_read);
            output.swap(temp_output);
        }
    }

    output[total_read] = '\0';  // Null-terminate the string

    // Close the pipe
    fclose(fp);

    return std::string(output.get());  // Caller is responsible for handling the output
}

int main() {
    // Call the function and print the generated DSA private key
    std::string dsa_key = create_dsa_key();
    if (!dsa_key.empty()) {
        std::cout << dsa_key;
    } else {
        std::cerr << "Failed to generate DSA key\n";
    }

    return 0;
}
