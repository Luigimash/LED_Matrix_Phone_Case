/*
notes:
-  Assume the "top" of each LED is the "positive" terminal for now

Order from top to bottom of LED pin numbers (ie. LED_0, LED_1, etc...)
5 4 3 9 2 8 1 7 0 6 22 16 23 24 21 14 19 26 18 15 20 28 17 25 13 27 12 10 11 

the entire display resolution is 20x28 pixels, 28 rows and 20 columns
*/

#include <stdio.h>
// later define a conversion from led_pins[] to actual GPIO pin number definitions (ie. A12, C5, etc)
int led_pins[] = {5, 4, 3, 9, 2, 8, 1, 7, 0, 6, 22, 16, 23, 24, 21, 14, 19, 26, 18, 15, 20, 28, 17, 25, 13, 27, 12, 10, 11};
#define LED_PINS_SIZE 29
#define NUM_ROWS 28
#define NUM_COLS 20
int matrix_pins[NUM_ROWS][NUM_COLS][2] = {0}; // 28 rows, 20 columns, 2 pins per cell (positive and negative). In 3rd dimension, 0 is positive pad, 1 is negative pad
    
// We assume the array defined by this array is positioned with (x,y)=(0,0) at the top left corner 

int main() {

    //For each LED in the 28x80 matrix display, need to determine the positive and negative pins 
    for (int i = 0; i < LED_PINS_SIZE; i++) {
        //Initial row for this LED pin is the index of the pin number from the led_pins[] array
        int row = i;
        int pin = led_pins[row]; //the pin number whose connections we're currently handling
        int direction = row % 2; //if 0, we start off ascending, if 1, we start descending
        for (int col = 0; col < NUM_COLS; col++) {
            //Typical case
            if (!direction) { // Ascending case, direction = 0
                if (row != NUM_ROWS) { //handling case that we *didn't* just flip direction at the bottom
                    matrix_pins[row][col][0] = pin;
                }
                // Positive for current row + negative for row above 
                if (row != 0) { //typical case except at very top
                    matrix_pins[row-1][col][1] = pin;
                    row--; //change row
                }
                else { //handling case of the current row being the topmost row
                    direction = 1; //flip the direction
                    //we don't change row when we flip the direction
                }
                //Increment to row above 
            }
            else { //Descending case, direction = 1
                // Positive for current row + Negative for row above 
                if (row != 0) { //handling case that we *didn't* just flip direction at the top
                    matrix_pins[row-1][col][1] = pin; 
                }            
                if (row != NUM_ROWS) { //typical case except at very bottom
                    matrix_pins[row][col][0] = pin; 
                    row++; 
                }
                else { //handling case of the current row being the bottommost row
                    direction = 0; //flip the direction
                }
            }
        }
    }

    // Write the matrix to a text file with fixed-width formatting for grid alignment
    FILE *file = fopen("matrix_pins.txt", "w");
    if (file == NULL) {
        fprintf(stderr, "Error: Could not open matrix_pins.txt for writing\n");
        return 1;
    }
    
    // Print the matrix with fixed-width cells for visual grid alignment
    // Format: (X,Y) with 2-digit padding for each number = 8 characters per cell
    for (int row = 0; row < NUM_ROWS; row++) {
        for (int col = 0; col < NUM_COLS; col++) {
            fprintf(file, "(%2d,%2d) ", matrix_pins[row][col][0], matrix_pins[row][col][1]);
        }
        fprintf(file, "\n");
    }
    
    fclose(file);
    printf("Matrix written to matrix_pins.txt\n");
    
    return 0;
}
