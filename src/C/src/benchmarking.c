#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "benchmarking.h"

void mat_mult(int outer_dim1, int outer_dim2, int inner_dim,
              double matrix1[outer_dim1][inner_dim],
              double matrix2[inner_dim][outer_dim2],
              double matrix3[outer_dim1][outer_dim2])
{

    for (int i = 0; i < outer_dim1; i++)
    {
        for (int j = 0; j < outer_dim2; j++)
        {
            matrix3[i][j] = matrix1[i][0] * matrix2[0][j];
            for (int k = 1; k < inner_dim; k++)
            {
                matrix3[i][j] += matrix1[i][k] * matrix2[k][j];
            }
        }
    }
}

void mat_mult_ikj(int outer_dim1, int outer_dim2, int inner_dim,
                  double matrix1[outer_dim1][inner_dim],
                  double matrix2[inner_dim][outer_dim2],
                  double matrix3[outer_dim1][outer_dim2])
{

    for (int i = 0; i < outer_dim1; i++)
    {
        for (int k = 0; k < inner_dim; k++)
        {
            for (int j = 0; j < outer_dim2; j++)
            {
                matrix3[i][j] += matrix1[i][k] * matrix2[k][j];
            }
        }
    }
}

void print_mat(int dim1, int dim2, double matrix[dim1][dim2])
{
    printf("[[");
    for (int i = 0; i < dim1; i++)
    {
        if (i != 0)
            printf(" [");
        for (int j = 0; j < dim2; j++)
        {
            if (j < dim2 - 1)
            {
                printf("%.8g ", matrix[i][j]);
            }
            else
                printf("%.8g", matrix[i][j]);
        }
        printf("]");
        if (i < dim1 - 1)
            printf("\n");
    }
    printf("]\n\n");
}

void serial_routine(int reps, int mat_dim, double matrix[mat_dim][mat_dim])
{
    for (int k = 0; k < reps; k++)
    {
        for (int i = 0; i < mat_dim; i++)
        {
            for (int j = 0; j < mat_dim; j++)
            {
                matrix[i][j] = i * mat_dim + j;
            }
        }
    }
}

void init_struct(int reps, int dims, int row_start, int row_end,
                 double mat[dims][dims])
{
    struct mat_data *data = &(struct mat_data){
        .reps = reps,
        .dims = dims,
        .mat = mat,
        .row_start = row_start,
        .row_end = row_end};
    parallel_routine(data);
}

void *parallel_routine(struct mat_data *data)
{
    // Assign struct array to variable of type pointer to array[NCOLS] of doubles
    double(*mat)[data->dims] = data->mat;

    for (int k = 0; k < data->reps; k++)
    {
        for (int i = data->row_start; i < data->row_end; i++)
        {
            for (int j = 0; j < data->dims; j++)
            {
                mat[i][j] = i * data->dims + j;
            }
        }
    }
    return NULL;
}

void multithreading_routine(int reps, int mat_dim, int n_threads,
                            double matrix[mat_dim][mat_dim])
{
    struct mat_data mat_blocks[n_threads];
    pthread_t threads[n_threads];

    for (int i = 0; i < n_threads; i++)
    {
        mat_blocks[i].reps = reps;
        mat_blocks[i].dims = mat_dim;
        mat_blocks[i].mat = matrix;
        mat_blocks[i].row_start = i * mat_dim / n_threads;
        mat_blocks[i].row_end = (i + 1) * mat_dim / n_threads;
    }

    for (int i = 0; i < n_threads; i++)
    {
        pthread_create(&threads[i], NULL, (void *)parallel_routine, (void *)&mat_blocks[i]);
    }

    for (int i = 0; i < n_threads; i++)
    {
        pthread_join(threads[i], NULL);
    }
}
