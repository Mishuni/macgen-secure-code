
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* write_results(const char* results) {
    // Create a temporary file
    char* temp_filename = tmpnam(NULL);
    if (temp_filename == NULL) {
        return NULL; // Handle error in generating temp filename
    }

    // Open the temporary file for writing
    FILE* temp_file = fopen(temp_filename, "w");
    if (temp_file == NULL) {
        return NULL; // Handle error in opening file
    }

    // Write the results to the temporary file
    fprintf(temp_file, "%s", results);

    // Close the file
    fclose(temp_file);

    // Return the dynamically allocated string containing the temporary file name
    char* result = malloc(strlen(temp_filename) + 1);
    if (result != NULL) {
        strcpy(result, temp_filename);
    }

    return result;
}