
'''
Tento skript bude sloužit jako výběr,
tedy uživatel si zde vybere jednotlive ukony a ty ho odkazou na dalsi skripty
'''

from assignment1 import assignment_1
from assignment2 import assignment_2
from index_coordinate import index_coordinates


def choose_assignment(assignment_input,indices_from_gui,volume1,volume2):
        print("You have XY options:\n1. Mixing two liquids.\n2. Dividing a larger volume into x beakers. \n3 ... \nTo select, enter a digit without a dot on the following line")

        #assignment = int(input("Write the digit you choose: "))
        #coords = index_coordinates(assignment)  # Get coordinates based on assignment
        assignment = int(assignment_input)  # Získejte číslo z GUI
        print(assignment)
    
        coords = index_coordinates(assignment,indices_from_gui)  # Get coordinates based on assignment

        # Set the coordinates
        coords_leftc = coords.get("leftovers")
        coords_watc = coords.get("water")
        coords_goalc = coords.get("goal beaker") 
        coords_beak1c = coords.get("beaker1")
        coords_beak2c = coords.get("beaker2", None) # beaker2 exists only for assignment 1

        print(coords_beak1c,coords_goalc,coords_beak2c,coords_leftc,coords_watc)

        

        if assignment == 1:
                assignment_1(volume1,volume2,coords_leftc,coords_watc,coords_goalc,coords_beak1c,coords_beak2c)
        elif assignment == 2:
                assignment_2(volume1,coords_leftc,coords_watc,coords_goalc,coords_beak1c)
        return coords_watc
