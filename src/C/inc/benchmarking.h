#ifndef MATRIX_MULT_H
#define MATRIX_MULT_H 1

struct mat_data
{
    int reps;
    int dims;
    double (*mat)[]; // Hack to allow a pointer to a VLA as a member of struct
    int row_start;
    int row_end;
};

/* Function declarations */
void mat_mult(int outer_dim1, int outer_dim2, int inner_dim,
              double matrix1[outer_dim1][inner_dim],
              double matrix2[inner_dim][outer_dim2],
              double matrix3[outer_dim1][outer_dim2]);

void print_mat(int dim1, int dim2, double matrix[dim1][dim2]);

void serial_routine(int reps, int mat_dim, double matrix[mat_dim][mat_dim]);

void init_struct(int reps, int dims, int row_start, int row_end,
                 double mat[dims][dims]);
void *parallel_routine(struct mat_data *data);

void multithreading_routine(int reps, int mat_dim, int n_threads,
                            double matrix[mat_dim][mat_dim]);

#endif