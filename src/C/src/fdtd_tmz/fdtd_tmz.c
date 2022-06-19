// Import user-defined headers
#include "fdtd_tmz.h"

// Import standard library headers
#include <stdlib.h>
#include <stdio.h>

/******************************************************************************
 *  Main
 ******************************************************************************/
int main(void)
{
    /* Run a scenario in C for debugging. */
    struct Grid *g = manual_tmzdemo(101, 81, 300);
    printf("TESTING");
    printf("%u", g->sizeX);
    return 0;
}