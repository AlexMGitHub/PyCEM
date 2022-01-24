#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <pthread.h>
#include "fdtd_tmz.h"

struct Grid *manual_tmzdemo(int sizeX, int sizeY, int max_time)
{
    /* Manually initialize struct Grid within C code rather than Python.
       Call tmzdemo(), and return the resulting pointer to struct Grid.
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

    tmzdemo(g);

    return g;
}

void tmzdemo(struct Grid *g)
{
    /* Reproduce John B. Schneider's C program from section 8.4 of his textbook
       Understanding the Finite-Difference Time-Domain Method.
    */
    for (g->time = 1; g->time < g->max_time; g->time++)
    {
        updateH2d(g); // Update magnetic field
        updateE2d(g); // Update electric field
        // Add source at center of grid
        EzG(g->time, g->sizeX / 2, g->sizeY / 2) = ezInc(g, 0.0);
    }
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

double ezInc(struct Grid *g, double location)
{
    /* Generate Ricker wavelet. */
    double arg;
    arg = M_PI * ((g->Cdtds * g->time - location) / PPW - 1.0);
    arg = arg * arg;
    return (1.0 - 2.0 * arg) * exp(-arg);
}