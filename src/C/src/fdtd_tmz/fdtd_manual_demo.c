// Import user-defined headers
#include "fdtd_tmz.h"

// Import standard library headers
#include <math.h>
#include <stdlib.h>

/******************************************************************************
 *  Manual TMZ Demo
 ******************************************************************************/
struct Grid *manual_tmzdemo(uint sizeX, uint sizeY, uint max_time)
{
    /* Manually initialize struct Grid within C code rather than Python.
       Call Ricker scenario, and return the resulting pointer to struct Grid.
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

    for (uint mm = 0; mm < g->sizeX; mm++)
        for (uint nn = 0; nn < g->sizeY - 1; nn++)
        {
            Chxh[mm][nn] = 1;
            Chxe[mm][nn] = g->Cdtds / imp0;
        }

    for (uint mm = 0; mm < g->sizeX - 1; mm++)
        for (uint nn = 0; nn < g->sizeY; nn++)
        {
            Chyh[mm][nn] = 1;
            Chye[mm][nn] = g->Cdtds / imp0;
        }

    for (uint mm = 0; mm < g->sizeX; mm++)
        for (uint nn = 0; nn < g->sizeY; nn++)
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

    // scenarioRicker(g);
    scenarioTFSF(g);

    return g;
}