#ifndef FDTD_TMZ_H
#define FDTD_TMZ_H 1

/* Headers */
#include <stdlib.h>
#include <stdio.h>

/* Macros */
#define ARR_SIZE (g->sizeX * g->sizeY)
#define EzG(TIME, MM, NN) *(g->Ez + (TIME)*ARR_SIZE + (MM)*g->sizeY + (NN))
#define EzLeft(M, Q, N) ezLeft[(N)*6 + (Q)*3 + (M)]
#define EzRight(M, Q, N) ezRight[(N)*6 + (Q)*3 + (M)]
#define EzTop(N, Q, M) ezTop[(M)*6 + (Q)*3 + (N)]
#define EzBottom(N, Q, M) ezBottom[(M)*6 + (Q)*3 + (N)]

#define ALLOC_1D(PNTR, NUM, TYPE)                                      \
    PNTR = (TYPE *)calloc(NUM, sizeof(TYPE));                          \
    if (!PNTR)                                                         \
    {                                                                  \
        perror("ALLOC_1D");                                            \
        fprintf(stderr,                                                \
                "Allocation failed for " #PNTR ".  Terminating...\n"); \
        exit(-1);                                                      \
    }

/* Structs */
struct Grid
{
    // Hack to allow a pointer to a VLA as a member of struct
    double (*Hx)[];
    double (*Chxh)[];
    double (*Chxe)[];

    double (*Hy)[];
    double (*Chyh)[];
    double (*Chye)[];

    double *Ez; // 3D array; use macro EzG to index
    double (*Ceze)[];
    double (*Cezh)[];

    uint sizeX;
    uint sizeY;
    uint time;
    uint max_time;
    double Cdtds;
};

struct Grid1D
{
    double *Hx, *Chxh, *Chxe;
    double *Hy, *Chyh, *Chye;
    double *Ez, *Ceze, *Cezh;

    uint sizeX;
    uint sizeY;
    uint time;
    uint max_time;
    double Cdtds;
};

/* Function prototypes */
// Boundaries
void initABC(struct Grid *g);
void updateABC(struct Grid *g);
// Grid
struct Grid *manual_tmzdemo(uint sizeX, uint sizeY, uint max_time);
// Scenarios
void scenarioRicker(struct Grid *g);
void scenarioTFSF(struct Grid *g);
void scenarioPlate(struct Grid *g);
void scenarioCircle(struct Grid *g);
void add_PEC_plate(struct Grid *g);
void add_PEC_disk(struct Grid *g);
// Sources
double updateRickerWavelet(struct Grid *g, double location);
double updateTFSFWavelet(struct Grid1D *g, double location);
void initTFSF(struct Grid *g, struct Grid1D *g1);
void updateTFSF(struct Grid *g, struct Grid1D *g1);
void gridInit1d(struct Grid1D *g);
// Updates
void updateH1d(struct Grid1D *g);
void updateE1d(struct Grid1D *g);
void updateH2d(struct Grid *g);
void updateE2d(struct Grid *g);
void *updateHx(struct Grid *g);
void *updateHy(struct Grid *g);
void *updateEz(struct Grid *g);
#endif