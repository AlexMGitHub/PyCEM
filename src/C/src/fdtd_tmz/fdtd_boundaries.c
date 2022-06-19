// Import user-defined headers
#include "fdtd_tmz.h"

// Import standard library headers
#include <math.h>
#include <stdlib.h>

/******************************************************************************
 *  Boundary Conditions
 ******************************************************************************/
static int initDone = 0;
static double coef0, coef1, coef2;
static double *ezLeft, *ezRight, *ezTop, *ezBottom;

void initABC(struct Grid *g)
{
    double temp1, temp2;

    double(*Chye)[g->sizeY] = g->Chye;
    double(*Cezh)[g->sizeY] = g->Cezh;

    initDone = 1;

    // allocate memory for ABC arrays //
    ALLOC_1D(ezLeft, g->sizeY * 6, double);
    ALLOC_1D(ezRight, g->sizeY * 6, double);
    ALLOC_1D(ezTop, g->sizeX * 6, double);
    ALLOC_1D(ezBottom, g->sizeX * 6, double);

    // calculate ABC coefficients //
    temp1 = sqrt(Cezh[0][0] * Chye[0][0]);
    temp2 = 1.0 / temp1 + 2.0 + temp1;
    coef0 = -(1.0 / temp1 - 2.0 + temp1) / temp2;
    coef1 = -2.0 * (temp1 - 1.0 / temp1) / temp2;
    coef2 = 4.0 * (temp1 + 1.0 / temp1) / temp2;

    return;
}

void updateABC(struct Grid *g)
{
    uint mm, nn;

    // ABC at left side of grid //
    for (nn = 0; nn < g->sizeY; nn++)
    {
        // clang-format off
        EzG(g->time, 0, nn) = 
            coef0 * (EzG(g->time, 2, nn) + EzLeft(0, 1, nn)) + 
            coef1 * (EzLeft(0, 0, nn) + EzLeft(2, 0, nn) 
                - EzG(g->time, 1, nn) - EzLeft(1, 1, nn)) + 
            coef2 * EzLeft(1, 0, nn) - EzLeft(2, 1, nn);

        // memorize old fields //
        for (mm = 0; mm < 3; mm++)
        {
            EzLeft(mm, 1, nn) = EzLeft(mm, 0, nn);
            EzLeft(mm, 0, nn) = EzG(g->time, mm, nn);
        }
    }

    // ABC at right side of grid //
    for (nn = 0; nn < g->sizeY; nn++)
    {
        EzG(g->time, g->sizeX - 1, nn) = 
            coef0 * (EzG(g->time, g->sizeX - 3, nn) + EzRight(0, 1, nn)) + 
            coef1 * (EzRight(0, 0, nn) + EzRight(2, 0, nn) 
                - EzG(g->time, g->sizeX - 2, nn) - EzRight(1, 1, nn)) + 
            coef2 * EzRight(1, 0, nn) - EzRight(2, 1, nn);

        // memorize old fields //
        for (mm = 0; mm < 3; mm++)
        {
            EzRight(mm, 1, nn) = EzRight(mm, 0, nn);
            EzRight(mm, 0, nn) = EzG(g->time, g->sizeX - 1 - mm, nn);
        }
    }

    // ABC at bottom of grid //
    for (mm = 0; mm < g->sizeX; mm++)
    {
        EzG(g->time, mm, 0) = 
            coef0 * (EzG(g->time, mm, 2) + EzBottom(0, 1, mm)) + 
            coef1 * (EzBottom(0, 0, mm) + EzBottom(2, 0, mm) 
                - EzG(g->time, mm, 1) - EzBottom(1, 1, mm)) + 
            coef2 * EzBottom(1, 0, mm) - EzBottom(2, 1, mm);

        // memorize old fields //
        for (nn = 0; nn < 3; nn++)
        {
            EzBottom(nn, 1, mm) = EzBottom(nn, 0, mm);
            EzBottom(nn, 0, mm) = EzG(g->time, mm, nn);
        }
    }

    // ABC at top of grid //
    for (mm = 0; mm < g->sizeX; mm++)
    {
        EzG(g->time, mm, g->sizeY - 1) = 
            coef0 * (EzG(g->time, mm, g->sizeY - 3) + EzTop(0, 1, mm)) + 
            coef1 * (EzTop(0, 0, mm) + EzTop(2, 0, mm) 
                - EzG(g->time, mm, g->sizeY - 2) - EzTop(1, 1, mm)) + 
            coef2 * EzTop(1, 0, mm) - EzTop(2, 1, mm);

        // memorize old fields //
        for (nn = 0; nn < 3; nn++)
        {
            EzTop(nn, 1, mm) = EzTop(nn, 0, mm);
            EzTop(nn, 0, mm) = EzG(g->time, mm, g->sizeY - 1 - nn);
        }
    }
    // clang-format on
    return;
}