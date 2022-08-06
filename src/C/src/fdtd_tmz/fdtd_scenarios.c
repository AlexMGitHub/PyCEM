// Import user-defined headers
#include "fdtd_tmz.h"

// Import standard library headers

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
    initTFSF(g, g1, 5, 95, 5, 75);  // Initialize total field/scattered field source

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
    initTFSF(g, g1, 5, 95, 5, 75);  // Initialize total field/scattered field source

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
    initTFSF(g, g1, 5, 95, 5, 75);  // Initialize total field/scattered field source

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
    initTFSF(g, g1, 5, 95, 5, 75);  // Initialize total field/scattered field source

    for (g->time = 1; g->time < g->max_time; g->time++)
    {
        updateH2d(g);      // Update magnetic field
        updateTFSF(g, g1); // Update total field/scattered field
        updateE2d(g);      // Update electric field
        updateABC(g);      // Update absorbing boundary condition
    }
}

void scenarioMinefield(struct Grid *g)
{
    /* TMz simulation with TFSF source and mulitple circular scatterers.*/

    struct Grid1D *g1;
    ALLOC_1D(g1, 1, struct Grid1D); // allocate memory for 1D Grid
    add_minefield_scatterers(g);    // add multiple circular scatterers
    initABC(g);                     // Initialize absorbing boundary condition
    initTFSF(g, g1, 5, 95, 5, 75);  // Initialize total field/scattered field source

    for (g->time = 1; g->time < g->max_time; g->time++)
    {
        updateH2d(g);      // Update magnetic field
        updateTFSF(g, g1); // Update total field/scattered field
        updateE2d(g);      // Update electric field
        updateABC(g);      // Update absorbing boundary condition
    }
}