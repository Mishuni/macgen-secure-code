
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>

void print_rand_num_plus_offset(int offset) {
    // Validate the offset to prevent potential overflow
    if (offset < 0 || offset > INT_MAX - 1) {
        return; // Invalid offset, do nothing
    }

    // Use a secure random number generator
    srand((unsigned int)time(NULL)); // Seed the PRNG with the current time
    int random_number = rand() % (INT_MAX - offset); // Generate a random number

    // Print the result
    printf("%d\n", random_number + offset);
}