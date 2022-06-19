// Import user-defined headers
#include "fdtd_tmz.h"

// Import standard library headers
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

/* Constants */
const double PPW = 20;

/******************************************************************************
 *  Sources
 ******************************************************************************/
double updateRickerWavelet(struct Grid *g, double location)
{
    /* Generate Ricker wavelet. */
    double arg;
    arg = M_PI * ((g->Cdtds * g->time - location) / PPW - 1.0);
    arg = arg * arg;
    return (1.0 - 2.0 * arg) * exp(-arg);
}

double updateTFSFWavelet(struct Grid1D *g, double location)
{
    /* Generate TFSF wavelet. */
    double arg;
    arg = M_PI * ((g->Cdtds * g->time - location) / PPW - 1.0);
    arg = arg * arg;
    return (1.0 - 2.0 * arg) * exp(-arg);
}

void initTFSF(struct Grid *g, struct Grid1D *g1)
{
    g1->Cdtds = g->Cdtds;
    g1->time = g->time;
    g1->max_time = g->max_time;
    g1->sizeX = g->sizeX;
    g1->sizeY = g->sizeY;

    gridInit1d(g1); // initialize 1d grid

    return;
}

void updateTFSF(struct Grid *g, struct Grid1D *g1)
{
    uint mm, nn;
    double(*Hy)[g->sizeY] = g->Hy;
    double(*Chye)[g->sizeY] = g->Chye;
    double(*Hx)[g->sizeY - 1] = g->Hx;
    double(*Chxe)[g->sizeY - 1] = g->Chxe;
    double(*Cezh)[g->sizeY] = g->Cezh;

    uint firstX = 5, firstY = 5, // indices for first point in TF region /*@\label{tfsftmzA}@*/
        lastX = 95, lastY = 75;  // indices for last point in TF region  /*@\label{tfsftmzB}@*/

    // check if tfsfInit() has been called
    if (firstX <= 0)
    {
        fprintf(stderr,
                "tfsfUpdate: tfsfInit must be called before tfsfUpdate.\n"
                "            Boundary location must be set to positive value.\n");
        exit(-1);
    }

    // correct Hy along left edge
    mm = firstX - 1;
    for (nn = firstY; nn <= lastY; nn++)
        Hy[mm][nn] -= Chye[mm][nn] * g1->Ez[mm + 1];

    // correct Hy along right edge
    mm = lastX;
    for (nn = firstY; nn <= lastY; nn++)
        Hy[mm][nn] += Chye[mm][nn] * g1->Ez[mm];

    // correct Hx along the bottom
    nn = firstY - 1;
    for (mm = firstX; mm <= lastX; mm++)
        Hx[mm][nn] += Chxe[mm][nn] * g1->Ez[mm];

    // correct Hx along the top
    nn = lastY;
    for (mm = firstX; mm <= lastX; mm++)
        Hx[mm][nn] -= Chxe[mm][nn] * g1->Ez[mm];

    updateH1d(g1);                          // update 1D magnetic field
    updateE1d(g1);                          // update 1D electric field
    g1->Ez[0] = updateTFSFWavelet(g1, 0.0); // set source node
    g1->time++;                             // increment time in 1D grid

    // correct Ez adjacent to TFSF boundary //
    // correct Ez field along left edge
    mm = firstX;
    for (nn = firstY; nn <= lastY; nn++)
        EzG(g->time - 1, mm, nn) -= Cezh[mm][nn] * g1->Hy[mm - 1];

    // correct Ez field along right edge
    mm = lastX;
    for (nn = firstY; nn <= lastY; nn++)
        EzG(g->time - 1, mm, nn) += Cezh[mm][nn] * g1->Hy[mm];

    // no need to correct Ez along top and bottom since
    // incident Hx is zero

    return;
}

void gridInit1d(struct Grid1D *g)
{
    double imp0 = 377.0, depthInLayer, lossFactor;
    uint mm;
    uint NLOSS = 20;
    double MAX_LOSS = 0.35;
    g->sizeX += NLOSS; // size of domain /*@\label{grid1dezA}@*/
    uint SizeX = g->sizeX;

    // Type = oneDGrid;   // set grid type  /*@\label{grid1dezB}@*/

    ALLOC_1D(g->Hy, SizeX - 1, double); /*@\label{grid1dezC}@*/
    ALLOC_1D(g->Chyh, SizeX - 1, double);
    ALLOC_1D(g->Chye, SizeX - 1, double);
    ALLOC_1D(g->Ez, SizeX, double);
    ALLOC_1D(g->Ceze, SizeX, double);
    ALLOC_1D(g->Cezh, SizeX, double); /*@\label{grid1dezD}@*/

    /* set the electric- and magnetic-field update coefficients */
    for (mm = 0; mm < SizeX - 1; mm++)
    { /*@\label{grid1dezE}@*/
        if (mm < SizeX - 1 - NLOSS)
        {
            g->Ceze[mm] = 1.0;
            g->Cezh[mm] = g->Cdtds * imp0;
            g->Chyh[mm] = 1.0;
            g->Chye[mm] = g->Cdtds / imp0;
        }
        else
        {
            depthInLayer = mm - (SizeX - 1 - NLOSS) + 0.5;
            lossFactor = MAX_LOSS * pow(depthInLayer / NLOSS, 2);
            g->Ceze[mm] = (1.0 - lossFactor) / (1.0 + lossFactor);
            g->Cezh[mm] = g->Cdtds * imp0 / (1.0 + lossFactor);
            depthInLayer += 0.5;
            lossFactor = MAX_LOSS * pow(depthInLayer / NLOSS, 2);
            g->Chyh[mm] = (1.0 - lossFactor) / (1.0 + lossFactor);
            g->Chye[mm] = g->Cdtds / imp0 / (1.0 + lossFactor);
        }
    }

    return;
}