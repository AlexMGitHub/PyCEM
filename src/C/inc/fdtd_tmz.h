#ifndef FDTD_TMZ_H
#define FDTD_TMZ_H 1

/* Macros */
#define ARR_SIZE (g->sizeX * g->sizeY)
#define EzG(TIME, MM, NN) *(g->Ez + (TIME)*ARR_SIZE + (MM)*g->sizeY + (NN))

/* Constants */
const double PPW = 20;

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

    int sizeX;
    int sizeY;
    int time;
    int max_time;
    double Cdtds;
};

/* Function prototypes */
struct Grid *manual_tmzdemo();
void tmzdemo(struct Grid *g);
void updateH2d(struct Grid *g);
void updateE2d(struct Grid *g);
void *updateHx(struct Grid *g);
void *updateHy(struct Grid *g);
void *updateEz(struct Grid *g);
double ezInc(struct Grid *g, double location);

#endif