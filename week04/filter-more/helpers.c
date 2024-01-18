#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int row = 0; row < height; row++)
    {
        for (int col = 0; col < width; col++)
        {
            int avg = round((image[row][col].rgbtRed + image[row][col].rgbtGreen + image[row][col].rgbtBlue) / 3.0);
            image[row][col].rgbtRed = image[row][col].rgbtGreen = image[row][col].rgbtBlue = avg;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    // Making a massive for original image
    RGBTRIPLE original[height][width];

    // Cycle for making a rmoeflective image
    for (int row = 0; row < height; row++)
    {
        for (int col = 0; col < width; col++)
        {
            original[row][col] = image[row][col];
        }
    }
    // Cycle for making a new reflective image
    for (int row = 0; row < height; row++)
    {
        for (int col = 0, swap = width - 1; col < width; col++)
        {
            image[row][col] = original[row][swap];
            swap--;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{

    RGBTRIPLE original[height][width];

    for (int row = 0; row < height; row++)
    {
        for (int col = 0; col < width; col++)
        {
            original[row][col] = image[row][col];
        }
    }

    float totalr, totalg, totalb;
    int count = 0;
    totalr = totalg = totalb = 0;

    for (int row = 0; row < height; row++)
    {
        for (int col = 0; col < width; col++)
        {
            for (int arrrow = row - 1; arrrow <= row + 1; arrrow++)
            {
                for (int arrcol = col - 1; arrcol <= col + 1; arrcol++)
                {
                    if (arrcol < width && arrrow < height && arrcol >= 0 && arrrow >= 0)
                    {
                        totalr += original[arrrow][arrcol].rgbtRed;
                        totalg += original[arrrow][arrcol].rgbtGreen;
                        totalb += original[arrrow][arrcol].rgbtBlue;
                        count++;
                    }
                }
            }
            image[row][col].rgbtRed = round(totalr / count);
            image[row][col].rgbtGreen = round(totalg / count);
            image[row][col].rgbtBlue = round(totalb / count);
            count = 0;
            totalr = totalg = totalb = 0;
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE old_image[height][width];

    for (int row = 0; row < height; row++)
    {
        for (int col = 0; col < width; col++)
        {
            old_image[row][col] = image[row][col];
        }
    }

    int gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};

    int gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    for (int row = 0; row < height; row++)
    {
        for (int col = 0; col < width; col++)
        {
            int mrow[3] = {row - 1, row, row + 1};
            int mcol[3] = {col - 1, col, col + 1};
            int gxr, gxg, gxb;
            gxr = gxg = gxb = 0;
            int gyr, gyg, gyb;
            gyr = gyg = gyb = 0;

            for (int rowcount = 0; rowcount < 3; rowcount++)
            {
                for (int colcount = 0; colcount < 3; colcount++)
                {
                    int nrow = mrow[rowcount];
                    int ncol = mcol[colcount];
                    RGBTRIPLE pixel = old_image[nrow][ncol];

                    if (nrow < height && nrow >= 0 && ncol < width && ncol >= 0)
                    {
                        gxr += pixel.rgbtRed * gx[rowcount][colcount];
                        gxg += pixel.rgbtGreen * gx[rowcount][colcount];
                        gxb += pixel.rgbtBlue * gx[rowcount][colcount];

                        gyr += pixel.rgbtRed * gy[rowcount][colcount];
                        gyg += pixel.rgbtGreen * gy[rowcount][colcount];
                        gyb += pixel.rgbtBlue * gy[rowcount][colcount];
                    }
                }
            }

            int newr = round(sqrt(gxr * gxr + gyr * gyr));
            int newg = round(sqrt(gxg * gxg + gyg * gyg));
            int newb = round(sqrt(gxb * gxb + gyb * gyb));

            image[row][col].rgbtRed = newr > 255 ? 255 : newr;
            image[row][col].rgbtGreen = newg > 255 ? 255 : newg;
            image[row][col].rgbtBlue = newb > 255 ? 255 : newb;
        }
    }
    return;
}
