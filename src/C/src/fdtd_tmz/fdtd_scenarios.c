// Import user-defined headers
#include "fdtd_tmz.h"

// Import standard library headers
#include <math.h>
#include <stdlib.h>

/******************************************************************************
 *  Scenarios
 ******************************************************************************/
void scenarioRicker(struct Grid *g)
{
    /* Reproduce John B. Schneider's C program from section 8.4 of his textbook
       Understanding the Finite-Difference Time-Domain Method.
    */
    for (g->time = 1; g->time < g->max_time; g->time++)
    {
        updateH2d(g); // Update magnetic field
        updateE2d(g); // Update electric field
        // Update Ricker Wavelet source at center of grid
        EzG(g->time, g->sizeX / 2, g->sizeY / 2) = updateRickerWavelet(g, 0.0);
    }
}

void scenarioTFSF(struct Grid *g)
{
    /* TMz simulation with TFSF source at left side of grid.

       Reproduces Fig. 8.6 from John B. Schneider's textbook
       Understanding the Finite-Difference Time-Domain Method.
    */

    struct Grid1D *g1;
    ALLOC_1D(g1, 1, struct Grid1D); // allocate memory for 1D Grid
    initABC(g);                     // Initialize absorbing boundary condition
    initTFSF(g, g1);                // Initialize total field/scattered field source

    for (g->time = 1; g->time < g->max_time; g->time++)
    {
        updateH2d(g);      // Update magnetic field
        updateTFSF(g, g1); // Update total field/scattered field
        updateE2d(g);      // Update electric field
        updateABC(g);      // Update absorbing boundary condition
    }
}

void scenarioPlate(struct Grid *g)
{
    /* TMz simulation with TFSF source and vertical PEC plate.

    Reproduces Fig. 8.7 from John B. Schneider's textbook
    Understanding the Finite-Difference Time-Domain Method.
    */

    struct Grid1D *g1;
    ALLOC_1D(g1, 1, struct Grid1D); // allocate memory for 1D Grid
    add_PEC_plate(g);               // add vertical PEC plate to grid
    initABC(g);                     // Initialize absorbing boundary condition
    initTFSF(g, g1);                // Initialize total field/scattered field source

    for (g->time = 1; g->time < g->max_time; g->time++)
    {
        updateH2d(g);      // Update magnetic field
        updateTFSF(g, g1); // Update total field/scattered field
        updateE2d(g);      // Update electric field
        updateABC(g);      // Update absorbing boundary condition
    }
}

void scenarioCircle(struct Grid *g)
{
    /* TMz simulation with TFSF source and PEC circle.

    Reproduces Fig. 8.14 from John B. Schneider's textbook
    Understanding the Finite-Difference Time-Domain Method.
    */

    struct Grid1D *g1;
    ALLOC_1D(g1, 1, struct Grid1D); // allocate memory for 1D Grid
    add_PEC_disk(g);                // add circular PEC disk to grid
    initABC(g);                     // Initialize absorbing boundary condition
    initTFSF(g, g1);                // Initialize total field/scattered field source

    for (g->time = 1; g->time < g->max_time; g->time++)
    {
        updateH2d(g);      // Update magnetic field
        updateTFSF(g, g1); // Update total field/scattered field
        updateE2d(g);      // Update electric field
        updateABC(g);      // Update absorbing boundary condition
    }
}

void scenarioCornerReflector(struct Grid *g)
{
    /* TMz simulation with TFSF source and a corner reflector.*/

    struct Grid1D *g1;
    ALLOC_1D(g1, 1, struct Grid1D); // allocate memory for 1D Grid
    add_corner_reflector(g);        // add corner reflector to grid
    initABC(g);                     // Initialize absorbing boundary condition
    initTFSF(g, g1);                // Initialize total field/scattered field source

    for (g->time = 1; g->time < g->max_time; g->time++)
    {
        updateH2d(g);      // Update magnetic field
        updateTFSF(g, g1); // Update total field/scattered field
        updateE2d(g);      // Update electric field
        updateABC(g);      // Update absorbing boundary condition
    }
}

/******************************************************************************
 *  Scatterers
 ******************************************************************************/
void add_PEC_plate(struct Grid *g)
{
    /* Create vertical PEC plate scatterer. */

    double(*Cezh)[g->sizeY] = g->Cezh;
    double(*Ceze)[g->sizeY] = g->Ceze;

    uint pec_left_offset = 20;
    uint pec_bottom_offset = 20;
    uint pec_top_offset = 20;

    for (uint nn = pec_bottom_offset; nn < g->sizeY - pec_top_offset; nn++)
    {
        Ceze[pec_left_offset][nn] = 0;
        Cezh[pec_left_offset][nn] = 0;
    }

    return;
}

void add_PEC_disk(struct Grid *g)
{
    /* Create circular PEC disk scatterer. */

    double(*Cezh)[g->sizeY] = g->Cezh;
    double(*Ceze)[g->sizeY] = g->Ceze;

    uint rad = 12;
    uint xCenter = g->sizeX / 2;
    uint yCenter = g->sizeY / 2;
    int xLocation, yLocation;

    for (uint mm = 1; mm < g->sizeX - 1; mm++)
    {
        xLocation = (int)mm - (int)xCenter;
        for (uint nn = 1; nn < g->sizeY - 1; nn++)
        {
            yLocation = (int)nn - (int)yCenter;
            if ((pow(xLocation, 2) + pow(yLocation, 2)) < pow(rad, 2))
            {
                Ceze[mm][nn] = 0;
                Cezh[mm][nn] = 0;
            }
        }
    }

    return;
}

void add_corner_reflector(struct Grid *g)
{
    /* Create corner reflector scatterer. */

    double(*Cezh)[g->sizeY] = g->Cezh;
    double(*Ceze)[g->sizeY] = g->Ceze;

    uint xCenter = g->sizeX / 2;
    uint yCenter = g->sizeY / 2;

    uint nnlow = (uint)(yCenter * 0.5);
    uint nnhigh = (uint)(yCenter * 1.5);
    for (uint mm = xCenter; mm <= (uint)(xCenter * 1.5); mm++)
    {
        if (nnlow <= yCenter)
        {
            Ceze[mm][nnlow] = 0;
            Cezh[mm][nnlow] = 0;
            Ceze[mm][nnhigh] = 0;
            Cezh[mm][nnhigh] = 0;
            nnlow++;
            nnhigh--;
        }
        else
        {
            break;
        }
    }

    return;
}