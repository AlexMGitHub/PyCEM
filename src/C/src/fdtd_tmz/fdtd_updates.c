// Import user-defined headers
#include "fdtd_tmz.h"

// Import standard library headers
#include <math.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

/******************************************************************************
 *  Field Updates
 ******************************************************************************/
void updateH2d(struct Grid *g)
{
    /* The X and Y components of the H-field updates are independent can be
       performed in parallel using separate threads.
    */
    pthread_t threadX;
    pthread_t threadY;

    pthread_create(&threadX, NULL, (void *)updateHx, (void *)g);
    pthread_create(&threadY, NULL, (void *)updateHy, (void *)g);

    pthread_join(threadX, NULL);
    pthread_join(threadY, NULL);
}

void updateE2d(struct Grid *g)
{
    /* Wrapper for electric field update.  Could be modified for parallel
       execution of multiple electric field components when relevant.
    */
    updateEz(g);
}

void *updateHx(struct Grid *g)
{
    /* Update X component of magnetic field. */
    double(*Hx)[g->sizeY - 1] = g->Hx;
    double(*Chxh)[g->sizeY - 1] = g->Chxh;
    double(*Chxe)[g->sizeY - 1] = g->Chxe;
    for (uint mm = 0; mm < g->sizeX; mm++)
        for (uint nn = 0; nn < g->sizeY - 1; nn++)
            Hx[mm][nn] = Chxh[mm][nn] * Hx[mm][nn] -
                         Chxe[mm][nn] * (EzG(g->time - 1, mm, nn + 1) - EzG(g->time - 1, mm, nn));
    return NULL;
}

void *updateHy(struct Grid *g)
{
    /* Update Y component of magnetic field. */
    double(*Hy)[g->sizeY] = g->Hy;
    double(*Chyh)[g->sizeY] = g->Chyh;
    double(*Chye)[g->sizeY] = g->Chye;
    for (uint mm = 0; mm < g->sizeX - 1; mm++)
        for (uint nn = 0; nn < g->sizeY; nn++)
            Hy[mm][nn] = Chyh[mm][nn] * Hy[mm][nn] +
                         Chye[mm][nn] * (EzG(g->time - 1, mm + 1, nn) - EzG(g->time - 1, mm, nn));
    return NULL;
}

void *updateEz(struct Grid *g)
{
    /* Update Z component of electric field. */
    double(*Hx)[g->sizeY - 1] = g->Hx;
    double(*Hy)[g->sizeY] = g->Hy;
    double(*Cezh)[g->sizeY] = g->Cezh;
    double(*Ceze)[g->sizeY] = g->Ceze;
    for (uint mm = 1; mm < g->sizeX - 1; mm++)
        for (uint nn = 1; nn < g->sizeY - 1; nn++)
            EzG(g->time, mm, nn) = Ceze[mm][nn] * EzG(g->time - 1, mm, nn) +
                                   Cezh[mm][nn] * ((Hy[mm][nn] - Hy[mm - 1][nn]) -
                                                   (Hx[mm][nn] - Hx[mm][nn - 1]));
    return NULL;
}

void updateH1d(struct Grid1D *g)
{
    /* The X and Y components of the H-field updates are independent can be
       performed in parallel using separate threads.
    */
    for (uint mm = 0; mm < g->sizeX - 1; mm++)
        g->Hy[mm] = g->Chyh[mm] * g->Hy[mm] + g->Chye[mm] * (g->Ez[mm + 1] - g->Ez[mm]);
}

void updateE1d(struct Grid1D *g)
{
    /* Wrapper for electric field update.  Could be modified for parallel
       execution of multiple electric field components when relevant.
    */
    /* Update Z component of electric field. */
    for (uint mm = 1; mm < g->sizeX - 1; mm++)
        g->Ez[mm] = g->Ceze[mm] * g->Ez[mm] + g->Cezh[mm] * (g->Hy[mm] - g->Hy[mm - 1]);
}