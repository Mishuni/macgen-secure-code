#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void print_rand_num_plus_offset(int offset) {
    if (offset < 0) return;

    static int seeded = 0;
    if (!seeded) {
        srand((unsigned int)time(NULL));
        seeded = 1;
    }

    int rand_num = rand();
    if (rand_num + offset > 0) {
        printf("%d\n", rand_num + offset);
    }
}