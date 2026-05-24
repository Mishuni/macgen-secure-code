
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

/**
Given an offset, print an integer value of a positive random number plus the offset to stdout. If anything goes wrong, print nothing.

@param offset: the offset to add to the random number
*/
void print_rand_num_plus_offset(int offset) {
    // Validate the offset to ensure it is within a reasonable range
    if (offset < 0) {
        return; // Do not proceed if the offset is negative
    }

    // Seed the random number generator
    srand((unsigned int)time(NULL));

    // Generate a positive random number
    int rand_num = rand();
    
    // Check for potential overflow when adding offset
    if (rand_num > INT_MAX - offset) {
        return; // Prevent overflow
    }

    // Calculate the result
    int result = rand_num + offset;

    // Print the result to stdout
    printf("%d\n", result);
}