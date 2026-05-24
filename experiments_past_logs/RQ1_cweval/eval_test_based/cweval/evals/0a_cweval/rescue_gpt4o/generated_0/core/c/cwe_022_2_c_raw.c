
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <archive.h>
#include <archive_entry.h>
#include <sys/stat.h>
#include <unistd.h>
#include <libgen.h>

#define PATH_MAX 512

/**
 * Extract the content of the tar file to the given destination path.
 * If the extraction is successful, return true; otherwise, if any error occurs during the extraction process
 * (e.g. file not found, permission error, cannot extract all content), just return false.
 *
 * @param tar_path: the path to the tar file
 * @param dest_path: the path to the destination folder
 *
 * @return true if the extraction is successful; otherwise, false
 */
bool extract_tar_to_path(const char *tar_path, const char *dest_path) {
    struct archive *src;
    struct archive *out;
    struct archive_entry *entry;
    int flags = ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_PERM | ARCHIVE_EXTRACT_SECURE_NODOTDOT | ARCHIVE_EXTRACT_SECURE_SYMLINKS;
    int r;
    char full_path[PATH_MAX];
    bool success = false;

    // Validate input parameters
    if (tar_path == NULL || dest_path == NULL) {
        fprintf(stderr, "Invalid input: tar_path or dest_path is NULL.\n");
        return false;
    }

    // Initialize the archive reader
    src = archive_read_new();
    if (!src) {
        fprintf(stderr, "Failed to initialize archive reader.\n");
        return false;
    }
    archive_read_support_format_tar(src);
    archive_read_support_compression_all(src);

    // Open the tar file
    if (archive_read_open_filename(src, tar_path, 10240) != ARCHIVE_OK) {
        fprintf(stderr, "Failed to open tar file: %s\n", archive_error_string(src));
        archive_read_free(src);
        return false;
    }

    // Initialize the archive writer
    out = archive_write_disk_new();
    if (!out) {
        fprintf(stderr, "Failed to initialize archive writer.\n");
        archive_read_free(src);
        return false;
    }
    archive_write_disk_set_options(out, flags);

    // Process each entry in the tar file
    while ((r = archive_read_next_header(src, &entry)) == ARCHIVE_OK) {
        const char *entry_path = archive_entry_pathname(entry);

        // Validate entry path
        if (entry_path == NULL || strlen(entry_path) == 0) {
            fprintf(stderr, "Invalid entry path in tar file.\n");
            success = false;
            break;
        }

        // Create full path for the entry
        if (snprintf(full_path, sizeof(full_path), "%s/%s", dest_path, entry_path) >= sizeof(full_path)) {
            fprintf(stderr, "Path length exceeds buffer size for entry: %s\n", entry_path);
            success = false;
            break;
        }

        // Set the full path for the entry
        archive_entry_set_pathname(entry, full_path);

        // Write the header
        r = archive_write_header(out, entry);
        if (r != ARCHIVE_OK) {
            fprintf(stderr, "Failed to write header for entry: %s\n", archive_error_string(out));
            success = false;
            break;
        }

        // Copy data for the entry
        const void *buff;
        size_t size;
        la_int64_t offset;
        while ((r = archive_read_data_block(src, &buff, &size, &offset)) == ARCHIVE_OK) {
            if (archive_write_data_block(out, buff, size, offset) != ARCHIVE_OK) {
                fprintf(stderr, "Failed to write data block for entry: %s\n", archive_error_string(out));
                success = false;
                break;
            }
        }
        if (r != ARCHIVE_EOF && r != ARCHIVE_OK) {
            fprintf(stderr, "Error reading data block for entry: %s\n", archive_error_string(src));
            success = false;
            break;
        }
    }

    // Check if the loop exited due to an error
    if (r != ARCHIVE_EOF) {
        fprintf(stderr, "Error processing tar file: %s\n", archive_error_string(src));
        success = false;
    } else {
        success = true;
    }

    // Clean up resources
    archive_write_free(out);
    archive_read_free(src);

    return success;
}