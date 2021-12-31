
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>
#include "matrix_mult.h"
//#include "../inc/matrix_mult.h"
// gcc -Wall -Wextra -Wconversion -Werror -o matrix_mult matrix_mult.c
// Create C extension for Python
// Unit test it
// Timeit vs Python for loops and numpy
// Then parallel algorithm

//gcc -c -Wall -Werror -fpic matrix_mult.c
//gcc -shared -o libmatrix_mult.so matrix_mult.o

//gcc -c -Wall -Werror -fpic cmult.c -I /usr/include/python3.7

/*int main(int argc, char *argv[])
{
    if (argc != 4)
        return EXIT_FAILURE;

    for (int i = 1; i < argc; i++)
    {
        //printf("argv[%.8g] = %s\n", i, argv[i]);
        if (!isNumber(argv[i]))
        {
            printf("ERROR");
            return EXIT_FAILURE;
        }
        printf("argv[%.8g] = %.8g\n", i, atoi(argv[i]));
    }
    int outer_dim1 = atoi(argv[1]);
    int outer_dim2 = atoi(argv[2]);
    int inner_dim = atoi(argv[3]);
*/
void matrix_mult(const int outer_dim1, const int outer_dim2, const int inner_dim,
                 double matrix1[outer_dim1][inner_dim],
                 double matrix2[inner_dim][outer_dim2],
                 double matrix3[outer_dim1][outer_dim2])
{
    /*
    int matrix1[outer_dim1][inner_dim];

    int matrix2[inner_dim][outer_dim2];

    int matrix3[outer_dim1][outer_dim2];

    int mat1_elements = outer_dim1 * inner_dim;

    for (int i = 0; i < outer_dim1; i++)
    {
        for (int j = 0; j < inner_dim; j++)
        {
            matrix1[i][j] = i * inner_dim + j;
        }
    }

    for (int i = 0; i < inner_dim; i++)
    {
        for (int j = 0; j < outer_dim2; j++)
        {
            matrix2[i][j] = i * outer_dim2 + j + mat1_elements;
        }
    }
*/
    mat_mult(outer_dim1, outer_dim2, inner_dim, matrix1, matrix2, matrix3);
    //print_mats(outer_dim1, outer_dim2, inner_dim, matrix1, matrix2, matrix3);
    //return EXIT_SUCCESS;
}

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
    //print_mat(outer_dim1, inner_dim, matrix1);
    //print_mat(inner_dim, outer_dim2, matrix2);
    //print_mat(outer_dim1, outer_dim2, matrix3);
    //print_mats(outer_dim1, outer_dim2, inner_dim,
    //         matrix1, matrix2, matrix3);
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

void print_mats(int outer_dim1, int outer_dim2, int inner_dim,
                double matrix1[outer_dim1][inner_dim],
                double matrix2[inner_dim][outer_dim2],
                double matrix3[outer_dim1][outer_dim2])
{
    for (int i = 0; i < outer_dim1; i++)
    {
        for (int j = 0; j < inner_dim; j++)
        {
            printf("%.8g ", matrix1[i][j]);
        }
        printf("\n");
    }
    printf("\n");
    for (int i = 0; i < inner_dim; i++)
    {
        for (int j = 0; j < outer_dim2; j++)
        {
            printf("%.8g ", matrix2[i][j]);
        }
        printf("\n");
    }
    printf("\n");
    for (int i = 0; i < outer_dim1; i++)
    {
        for (int j = 0; j < outer_dim2; j++)
        {
            printf("%.8g ", matrix3[i][j]);
        }
        printf("\n");
    }
    printf("\n");
}

bool isNumber(char number[])
{
    int i = 0;

    //checking for negative numbers
    if (number[0] == '-')
        i = 1;
    for (; number[i] != 0; i++)
    {
        //if (number[i] > '9' || number[i] < '0')
        if (!isdigit(number[i]))
            return false;
    }
    return true;
}