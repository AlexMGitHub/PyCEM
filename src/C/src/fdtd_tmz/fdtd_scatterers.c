// Import user-defined headers
#include "fdtd_tmz.h"

// Import standard library headers
#include <math.h>
#include <stdlib.h>

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

void add_minefield_scatterers(struct Grid *g)
{
    /* Create multiple circular scatterers. */

    double(*Cezh)[g->sizeY] = g->Cezh;
    double(*Ceze)[g->sizeY] = g->Ceze;

    const uint NUM_SCATTERERS = 5;
    uint rads[5] = {5, 12, 10, 8, 6};
    uint xCenters[5] = {g->sizeX / 8, g->sizeX / 3, g->sizeX / 2, 3 * g->sizeX / 4, 4 * g->sizeX / 5};
    uint yCenters[5] = {4 * g->sizeY / 5, 1 * g->sizeY / 3, 2 * g->sizeY / 3, 2 * g->sizeY / 5, 4 * g->sizeY / 5};
    int xLocation, yLocation;

    for (uint i = 0; i < NUM_SCATTERERS; i++)
    {
        for (uint mm = 1; mm < g->sizeX - 1; mm++)
        {
            xLocation = (int)mm - (int)xCenters[i];
            for (uint nn = 1; nn < g->sizeY - 1; nn++)
            {
                yLocation = (int)nn - (int)yCenters[i];
                if ((pow(xLocation, 2) + pow(yLocation, 2)) < pow(rads[i], 2))
                {
                    Ceze[mm][nn] = 0;
                    Cezh[mm][nn] = 0;
                }
            }
        }
    }

    return;
}