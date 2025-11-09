notes:
-  Assume the "top" of each LED is the "positive" terminal for now

Order from top to bottom of LED pin numbers (ie. LED_0, LED_1, etc...)
5 4 3 9 2 8 1 7 0 6 22 16 23 24 21 14 19 26 18 15 20 28 17 25 13 27 12 10 11 

the entire display resolution is 20x28 pixels, 28 rows and 20 columns


nix-shell -p gcc --run "gcc -o gen_matrix_pins gen_matrix_pins.c && ./gen_matrix_pins"
