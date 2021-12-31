#ifndef MATRIX_MULT_H
#define MATRIX_MULT_H 1

void matrix_mult(const int outer_dim1,
                 const int outer_dim2,
                 const int inner_dim,
                 double matrix1[outer_dim1][inner_dim],
                 double matrix2[inner_dim][outer_dim2],
                 double matrix3[outer_dim1][outer_dim2]);

void mat_mult(int outer_dim1, int outer_dim2, int inner_dim,
              double matrix1[outer_dim1][inner_dim],
              double matrix2[inner_dim][outer_dim2],
              double matrix3[outer_dim1][outer_dim2]);

void print_mat(int dim1, int dim2, double matrix[dim1][dim2]);

void print_mats(int outer_dim1, int outer_dim2, int inner_dim,
                double matrix1[outer_dim1][inner_dim],
                double matrix2[inner_dim][outer_dim2],
                double matrix3[outer_dim1][outer_dim2]);

bool isNumber(char number[]);

#endif