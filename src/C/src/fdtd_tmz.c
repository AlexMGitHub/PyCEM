#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <pthread.h>
#include "fdtd_tmz.h"

static double coef0, coef1, coef2;
static double *ezLeft, *ezRight, *ezTop, *ezBottom;

struct Grid *manual_tmzdemo(int sizeX, int sizeY, int max_time)
{
    /* Manually initialize struct Grid within C code rather than Python.
       Call rickerTMz2D(), and return the resulting pointer to struct Grid.
    */
    struct Grid *g = malloc(sizeof(struct Grid));
    double imp0 = 377.0;
    g->sizeX = sizeX;
    g->sizeY = sizeY;
    g->time = 0;
    g->max_time = max_time;
    g->Cdtds = 1.0 / sqrt(2.0);

    double(*Hx)[sizeY - 1] = calloc((size_t)(sizeX * (sizeY - 1)), sizeof(double));
    double(*Chxh)[sizeY - 1] = malloc(sizeof(double[sizeX][sizeY - 1]));
    double(*Chxe)[sizeY - 1] = malloc(sizeof(double[sizeX][sizeY - 1]));

    double(*Hy)[sizeY] = calloc(1, sizeof(double[sizeX - 1][sizeY]));
    double(*Chyh)[sizeY] = malloc(sizeof(double[sizeX - 1][sizeY]));
    double(*Chye)[sizeY] = malloc(sizeof(double[sizeX - 1][sizeY]));

    double *Ez = (double *)calloc((size_t)(max_time * sizeX * sizeY), sizeof(double));
    double(*Ceze)[sizeY] = malloc(sizeof(double[sizeX][sizeY]));
    double(*Cezh)[sizeY] = malloc(sizeof(double[sizeX][sizeY]));

    for (int mm = 0; mm < g->sizeX; mm++)
        for (int nn = 0; nn < g->sizeY - 1; nn++)
        {
            Chxh[mm][nn] = 1;
            Chxe[mm][nn] = g->Cdtds / imp0;
        }

    for (int mm = 0; mm < g->sizeX - 1; mm++)
        for (int nn = 0; nn < g->sizeY; nn++)
        {
            Chyh[mm][nn] = 1;
            Chye[mm][nn] = g->Cdtds / imp0;
        }

    for (int mm = 0; mm < g->sizeX; mm++)
        for (int nn = 0; nn < g->sizeY; nn++)
        {
            Ceze[mm][nn] = 1;
            Cezh[mm][nn] = g->Cdtds * imp0;
        }

    g->Hx = Hx;
    g->Chxh = Chxh;
    g->Chxe = Chxe;

    g->Hy = Hy;
    g->Chyh = Chyh;
    g->Chye = Chye;

    g->Ez = Ez;
    g->Ceze = Ceze;
    g->Cezh = Cezh;

    rickerTMz2D(g);

    return g;
}

void rickerTMz2D(struct Grid *g)
{
    /* Reproduce John B. Schneider's C program from section 8.4 of his textbook
       Understanding the Finite-Difference Time-Domain Method.
    */
    for (g->time = 1; g->time < g->max_time; g->time++)
    {
        updateH2d(g); // Update magnetic field
        updateE2d(g); // Update electric field
        // Add source at center of grid
        EzG(g->time, g->sizeX / 2, g->sizeY / 2) = rickerWavelet(g, 0.0);
    }
}

void initABC(struct Grid *g)
{
}

void updateABC(struct Grid *g)
{
}

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
    for (int mm = 0; mm < g->sizeX; mm++)
        for (int nn = 0; nn < g->sizeY - 1; nn++)
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
    for (int mm = 0; mm < g->sizeX - 1; mm++)
        for (int nn = 0; nn < g->sizeY; nn++)
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
    for (int mm = 1; mm < g->sizeX - 1; mm++)
        for (int nn = 1; nn < g->sizeY - 1; nn++)
            EzG(g->time, mm, nn) = Ceze[mm][nn] * EzG(g->time - 1, mm, nn) +
                                   Cezh[mm][nn] * ((Hy[mm][nn] - Hy[mm - 1][nn]) -
                                                   (Hx[mm][nn] - Hx[mm][nn - 1]));
    return NULL;
}

double rickerWavelet(struct Grid *g, double location)
{
    /* Generate Ricker wavelet. */
    double arg;
    arg = M_PI * ((g->Cdtds * g->time - location) / PPW - 1.0);
    arg = arg * arg;
    return (1.0 - 2.0 * arg) * exp(-arg);
}

#define EzLeft(M, Q, N) ezLeft[(N)*6 + (Q)*3 + (M)] /*@\label{abctmzA}@*/
#define EzRight(M, Q, N) ezRight[(N)*6 + (Q)*3 + (M)]
#define EzTop(N, Q, M) ezTop[(M)*6 + (Q)*3 + (N)]
#define EzBottom(N, Q, M) ezBottom[(M)*6 + (Q)*3 + (N)]

static int initDone = 0;
static double coef0, coef1, coef2;
static double *ezLeft, *ezRight, *ezTop, *ezBottom;

void abcInit(Grid *g)
{ /*@\label{abctmzB}@*/
    double temp1, temp2;

    initDone = 1;

    /* allocate memory for ABC arrays */
    ALLOC_1D(ezLeft, SizeY * 6, double);
    ALLOC_1D(ezRight, SizeY * 6, double);
    ALLOC_1D(ezTop, SizeX * 6, double);
    ALLOC_1D(ezBottom, SizeX * 6, double);

    /* calculate ABC coefficients */
    temp1 = sqrt(Cezh(0, 0) * Chye(0, 0)); /*@\label{abctmzC}@*/
    temp2 = 1.0 / temp1 + 2.0 + temp1;
    coef0 = -(1.0 / temp1 - 2.0 + temp1) / temp2;
    coef1 = -2.0 * (temp1 - 1.0 / temp1) / temp2;
    coef2 = 4.0 * (temp1 + 1.0 / temp1) / temp2;

    return;
}

void abc(Grid *g) /*@\label{abctmzD}@*/
{
    int mm, nn;

    /* ABC at left side of grid */
    for (nn = 0; nn < SizeY; nn++)
    {
        Ez(0, nn) = coef0 * (Ez(2, nn) + EzLeft(0, 1, nn)) + coef1 * (EzLeft(0, 0, nn) + EzLeft(2, 0, nn) - Ez(1, nn) - EzLeft(1, 1, nn)) + coef2 * EzLeft(1, 0, nn) - EzLeft(2, 1, nn);

        /* memorize old fields */
        for (mm = 0; mm < 3; mm++)
        {
            EzLeft(mm, 1, nn) = EzLeft(mm, 0, nn);
            EzLeft(mm, 0, nn) = Ez(mm, nn);
        }
    }

    /* ABC at right side of grid */
    for (nn = 0; nn < SizeY; nn++)
    {
        Ez(SizeX - 1, nn) = coef0 * (Ez(SizeX - 3, nn) + EzRight(0, 1, nn)) + coef1 * (EzRight(0, 0, nn) + EzRight(2, 0, nn) - Ez(SizeX - 2, nn) - EzRight(1, 1, nn)) + coef2 * EzRight(1, 0, nn) - EzRight(2, 1, nn);

        /* memorize old fields */
        for (mm = 0; mm < 3; mm++)
        {
            EzRight(mm, 1, nn) = EzRight(mm, 0, nn);
            EzRight(mm, 0, nn) = Ez(SizeX - 1 - mm, nn);
        }
    }

    /* ABC at bottom of grid */
    for (mm = 0; mm < SizeX; mm++)
    {
        Ez(mm, 0) = coef0 * (Ez(mm, 2) + EzBottom(0, 1, mm)) + coef1 * (EzBottom(0, 0, mm) + EzBottom(2, 0, mm) - Ez(mm, 1) - EzBottom(1, 1, mm)) + coef2 * EzBottom(1, 0, mm) - EzBottom(2, 1, mm);

        /* memorize old fields */
        for (nn = 0; nn < 3; nn++)
        {
            EzBottom(nn, 1, mm) = EzBottom(nn, 0, mm);
            EzBottom(nn, 0, mm) = Ez(mm, nn);
        }
    }

    /* ABC at top of grid */
    for (mm = 0; mm < SizeX; mm++)
    {
        Ez(mm, SizeY - 1) = coef0 * (Ez(mm, SizeY - 3) + EzTop(0, 1, mm)) + coef1 * (EzTop(0, 0, mm) + EzTop(2, 0, mm) - Ez(mm, SizeY - 2) - EzTop(1, 1, mm)) + coef2 * EzTop(1, 0, mm) - EzTop(2, 1, mm);

        /* memorize old fields */
        for (nn = 0; nn < 3; nn++)
        {
            EzTop(nn, 1, mm) = EzTop(nn, 0, mm);
            EzTop(nn, 0, mm) = Ez(mm, SizeY - 1 - nn);
        }
    }

    return;
}