from pipette_work import Program_1

def assignment_1(volume1, volume2,coords_leftc, coords_watc,coords_goalc,coords_beak1c,coords_beak2c):
    
    program1 = Program_1()
    
    try:
        # Get volume input from the user
        program1.home()

        # Perform washing between operations
        program1.wash(coords_leftc, coords_watc)

        # Process liquid 1
        program1.pipette_cycle(volume1, lambda vol: program1.liquid_1(vol, coords_goalc, coords_beak1c))

        # Perform washing between operations
        program1.wash(coords_leftc, coords_watc)
        # Perform washing between operations
        program1.wash(coords_leftc, coords_watc)
        

        # Process liquid 2
        program1.pipette_cycle(volume2, lambda vol: program1.liquid_2(vol, coords_goalc, coords_beak2c))

        # Perform washing between operations
        program1.wash(coords_leftc, coords_watc)
        
        program1.home_end()

    except KeyboardInterrupt:
        print("Operation interrupted by user.")
    finally:
        # Ensure resources are cleaned up
        program1.quit()

    

    #print(volume1,volume2)