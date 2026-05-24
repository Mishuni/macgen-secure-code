
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <limits.h>

/**
Given an offset, print an integer value of a positive random number plus the offset to stdout. If anything goes wrong, print nothing.

@param offset: the offset to add to the random number
*/
void print_rand_num_plus_offset(int offset) {
    // Ensure offset is non-negative
    if (offset < 0) {
        return;
    }

    // Generate a random number
    int rand_num = rand(); // rand() generates a non-negative integer in the range [0, RAND_MAX]

    // Check for overflow when adding offset to rand_num
    if (rand_num > INT_MAX - offset) {
        return; // Overflow would occur, so return without printing
    }

    // Calculate the result
    int result = rand_num + offset;

    // Print the result
    printf("%d\n", result);
}