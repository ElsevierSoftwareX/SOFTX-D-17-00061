/* File: example.i */
%module pixel_search

%{
#define SWIG_FILE_WITH_INIT
#include "pixel_search.h"
%}

%include "numpy.i"

%init %{
import_array();
%}

%apply (int DIM1, int DIM2, int DIM3, float* IN_ARRAY3) {(int h1, int w1, int d1, float *im1)};
%apply (int DIM1, int DIM2, int DIM3, float* IN_ARRAY3) {(int h2, int w2, int d2, float *im2)};
%apply (int DIM1, float* ARGOUT_ARRAY1) {(int n1, float *argoutdata)};

%include "pixel_search.h"
