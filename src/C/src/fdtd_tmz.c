#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <pthread.h>
#include <string.h>
#include "fdtd_tmz.h"
/*
static int initDone = 0;
static double coef0, coef1, coef2;
static double *ezLeft, *ezRight, *ezTop, *ezBottom;
static uint firstX = 0, firstY, // indices for first point in TF region
           lastX, lastY;       // indices for last point in TF region

static struct Grid1D *g1;  // 1D auxilliary grid

#define NLOSS     20   // number of lossy cells at end of 1D grid
#define MAX_LOSS  0.35 // maximum loss factor in lossy layer


void gridInit1d(struct Grid1D *g) {
  double imp0 = 377.0, depthInLayer, lossFactor;
  uint mm;

  g->sizeX += NLOSS;    // size of domain
  //Type = oneDGrid;   // set grid type

  ALLOC_1D(g->Hy,   g->sizeX - 1, double);
  ALLOC_1D(g->Chyh, g->sizeX - 1, double);
  ALLOC_1D(g->Chye, g->sizeX - 1, double);
  ALLOC_1D(g->Ez,   g->sizeX, double);
  ALLOC_1D(g->Ceze, g->sizeX, double);
  ALLOC_1D(g->Cezh, g->sizeX, double);

  // set the electric- and magnetic-field update coefficients //
  for (mm = 0; mm < g->sizeX - 1; mm++) {
    if (mm < g->sizeX - 1 - NLOSS) {
      g->Ez[mm] = 0.0;
      g->Ceze[mm] = 1.0;
      g->Cezh[mm] = g->Cdtds * imp0;
      g->Chyh[mm] = 1.0;
      g->Chye[mm] = g->Cdtds / imp0;
    } else {
      depthInLayer = mm - (g->sizeX - 1 - NLOSS) + 0.5;
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
}*/

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

       Reproduces Fig. 8.5 from John B. Schneider's textbook
       Understanding the Finite-Difference Time-Domain Method.
    */
    // struct Grid1D *g1 = malloc(sizeof(struct Grid1D));
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

// void scenarioPlate(struct Grid *g)
//{
/* TMz simulation with TFSF source and vertical PEC plate.

   Reproduces Fig. 8.6 from John B. Schneider's textbook
   Understanding the Finite-Difference Time-Domain Method.
*/
/*
initABC(g);          // Initialize absorbing boundary condition
initTFSF(g);         // Initialize total field/scattered field source
for (g->time = 1; g->time < g->max_time; g->time++)
{
  updateH2d(g);   // Update magnetic field
  updateTFSF(g);  // Update total field/scattered field
  updateE2d(g);   // Update electric field
  updateABC(g);   // Update absorbing boundary condition
}
}*/

// void scenarioCircle(struct Grid *g)
//{
/* TMz simulation with TFSF source and PEC circle.

   Reproduces Fig. 8.7 from John B. Schneider's textbook
   Understanding the Finite-Difference Time-Domain Method.
*/
//}

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

    // ALLOC_1D(g1, 1, struct Grid1D); // allocate memory for 1D Grid
    // memcpy(g1, g, sizeof(struct Grid)); // copy information from 2D array
    g1->Cdtds = g->Cdtds;
    g1->time = g->time;
    g1->max_time = g->max_time;
    g1->sizeX = g->sizeX;
    g1->sizeY = g->sizeY;

    gridInit1d(g1); // initialize 1d grid

    // ezIncInit(g); // initialize source function

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
        EzG(g->time, mm, nn) -= Cezh[mm][nn] * g1->Hy[mm - 1];

    // correct Ez field along right edge
    mm = lastX;
    for (nn = firstY; nn <= lastY; nn++)
        EzG(g->time, mm, nn) += Cezh[mm][nn] * g1->Hy[mm];

    // no need to correct Ez along top and bottom since
    // incident Hx is zero

    return;
}

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
        EzG(g->time, 0, nn) = coef0 * (EzG(g->time, 2, nn) + EzLeft(0, 1, nn)) + coef1 * (EzLeft(0, 0, nn) + EzLeft(2, 0, nn) - EzG(g->time, 1, nn) - EzLeft(1, 1, nn)) + coef2 * EzLeft(1, 0, nn) - EzLeft(2, 1, nn);

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
        EzG(g->time, g->sizeX - 1, nn) = coef0 * (EzG(g->time, g->sizeX - 3, nn) + EzRight(0, 1, nn)) + coef1 * (EzRight(0, 0, nn) + EzRight(2, 0, nn) - EzG(g->time, g->sizeX - 2, nn) - EzRight(1, 1, nn)) + coef2 * EzRight(1, 0, nn) - EzRight(2, 1, nn);

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
        EzG(g->time, mm, 0) = coef0 * (EzG(g->time, mm, 2) + EzBottom(0, 1, mm)) + coef1 * (EzBottom(0, 0, mm) + EzBottom(2, 0, mm) - EzG(g->time, mm, 1) - EzBottom(1, 1, mm)) + coef2 * EzBottom(1, 0, mm) - EzBottom(2, 1, mm);

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
        EzG(g->time, mm, g->sizeY - 1) = coef0 * (EzG(g->time, mm, g->sizeY - 3) + EzTop(0, 1, mm)) + coef1 * (EzTop(0, 0, mm) + EzTop(2, 0, mm) - EzG(g->time, mm, g->sizeY - 2) - EzTop(1, 1, mm)) + coef2 * EzTop(1, 0, mm) - EzTop(2, 1, mm);

        // memorize old fields //
        for (nn = 0; nn < 3; nn++)
        {
            EzTop(nn, 1, mm) = EzTop(nn, 0, mm);
            EzTop(nn, 0, mm) = EzG(g->time, mm, g->sizeY - 1 - nn);
        }
    }

    return;
}

void gridInit1d(struct Grid1D *g)
{
    double imp0 = 377.0, depthInLayer, lossFactor;
    uint mm;
    uint NLOSS = 20;
    double MAX_LOSS = 0.35;
    uint SizeX = g->sizeX;
    SizeX += NLOSS; // size of domain /*@\label{grid1dezA}@*/
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

/******************************************************************************
 *  Miscellaneous
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

int main(void)
{
    struct Grid *g = manual_tmzdemo(101, 81, 300);
    printf("TESTING");
    printf("%u", g->sizeX);
    return 0;
}