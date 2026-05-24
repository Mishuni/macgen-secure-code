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