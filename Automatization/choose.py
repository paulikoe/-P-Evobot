
'''
Tento skript bude sloužit jako výběr,
tedy uživatel si zde vybere jednotlive ukony a ty ho odkazou na dalsi skripty
'''
def chooseF():
    print("You have X options:\n1. Mixing two liquids.\n2. ... \nTo select, enter a digit without a dot on the following line")

    assignment = input ("Write the digit you choose: ")
    from ass1 import program1
    if assignment == 1:
        program1()