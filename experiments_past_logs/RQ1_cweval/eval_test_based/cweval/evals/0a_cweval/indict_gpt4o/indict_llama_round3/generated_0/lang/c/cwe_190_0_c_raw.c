
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>
#include <stdbool.h>

bool safe_add(int a, int b, int* result) {
    if ((b > 0) && (a > INT_MAX - b)) {
        return false; // Overflow
    }
    if ((b < 0) && (a < INT_MIN - b)) {
        return false; // Underflow
    }
    *result = a + b;
    return true;
}

void print_rand_num_plus_offset(int offset) {
    srand((unsigned int)time(NULL) ^ (uintptr_t)&offset); // Improved seeding for better randomness
    int random_number = rand() % 100 + 1; // Generate a random number between 1 and 100
    int result;

    if (safe_add(random_number, offset, &result)) {
        printf("%d\n", result);
    }
}