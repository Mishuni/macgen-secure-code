
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/**
Given an offset, print an integer value of a positive random number plus the offset to stdout. If anything goes wrong, print nothing.

@param offset: the offset to add to the random number
*/
void print_rand_num_plus_offset(int offset) {
    // Generate a secure random number between 1 and 100
    uint32_t random_number = arc4random_uniform(100) + 1;

    // Print the random number plus the offset
    printf("%d\n", random_number + offset);
}