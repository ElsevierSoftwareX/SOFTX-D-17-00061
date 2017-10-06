#include <stdio.h>
#include <math.h>
#include "pixel_search.h"

/* 2014-06-02 -- Rémi and Eddy -- program to calculate CC on two regular images
 This will certainly grow... */

/* Inputs (python side):
 *    - im1 (3D numpy array) -- Reference Image -- small
 *    - im2 (3D numpy array) -- Search range of other image -- should be at least as big as the reference pattern
 * 
 * Inputs (C side):
 *    - im1: 3 ints for dimensions + pointer to 1D-image
 *    - im2: 3 ints for dimensions + pointer to 1D-image
 * 
 * Returns:
 *    - CC float for the moment.
 *
 */


void pixel_search(  int slic1, int rows1, int cols1, float* im1,\
                    int slic2, int rows2, int cols2, float* im2,\
                    int n1, float* argoutdata )
{
    // int variable to build index to 1D-images from x,y,z coordinates
    int index1, index2;
    
    // loop variables for 3D search range
    int z, y, x;

    // loop variables for 3D CC calculation
    int k, j, i;

    // three components to our NCC calculation (see documentation/C-remi.odt)
    double a,b,c;

    
    // empty variables for each pixel of our 3D image    
    float im1px, im2px;
    
    // Variable to assemble NCC into.
    float cc;

    // Maximum variables, for tracking the best NCC so far...
    int z_max, y_max, x_max;
    float cc_max;

	// Initialization AFTER declaration for MSVC great compiler
	a = b = c = 0;
	z_max = y_max = x_max = 0;
	cc_max = 0;
	
    /* Go through search range in im2 -- z, y, x positions are offsets of the window,
         Consequently the first iteration here at z=y=x=0, is comparing im1 with the top
         Corner of im2
         Erika: add = to z<slic2-slic1 */
    for (z=0; z<=slic2-slic1; z++ )
    {
      for (y=0; y<=rows2-rows1; y++ )
      {
        for (x=0; x<=cols2-cols1; x++ )
        {
          // reset calculations
          a = b = c = 0;

          // CC calculation Loop z-first (for numpy)
          for (k=0; k<slic1; k++ )
          {
            for (j=0; j<rows1; j++ )
            {
              for (i=0; i<cols1; i++ )
              {
                // build index to 1D image
                index1 =   k  *rows1*cols1 +   j  *cols1 +   i;
                index2 = (k+z)*rows2*cols2 + (j+y)*cols2 + (i+x);

                // fetch 1 pixel from both images
                im1px = im1[ index1 ];
                im2px = im2[ index2 ];

                // Our little bits of the NCC
                a = a +    im1px * im2px;
                b = b +    im1px * im1px;
                c = c +    im2px * im2px;
              }
            }
          }
          // End CC calculation loop

          // once the sums are done, add up and sqrt
          // assemble bits and calculate CC
          
          cc = a / sqrt( b * c);
//           printf( "\tC: pixel_search: cc = %f\n", cc );

          //printf( "\t-> CC@(z=%i,y=%i,x=%i) = %f\n", z, y, x, cc );
          
          // If this cc is higher than the previous best, update our best...
          if ( cc > cc_max )
          {
            x_max   = x;
            y_max   = y;
            z_max   = z;
            cc_max  = cc;
            //printf("##### CC UPDATED #####");
            //printf( "\t-> New CC_max@(z=%i,y=%i,x=%i) = %f\n", z_max, y_max, x_max, cc );
          }
        }
      }
    }

    argoutdata[ 0 ] = (float) z_max;
    argoutdata[ 1 ] = (float) y_max;
    argoutdata[ 2 ] = (float) x_max;
    argoutdata[ 3 ] = cc_max;

//     return cc_max;
}

