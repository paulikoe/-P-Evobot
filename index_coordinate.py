# prirazeni_zadaneho_indexu_ke_kadince_finale
'''
#leftovers
leftc = int(input("Write index of beaker for leftovers: "))
watc = int(input("Write index of beaker for water: "))
goalc = int(input("Write index of beaker for goal_beaker: "))
beak1c = int(input("Write index of beaker for beaker1: "))
beak2c = int(input("Write index of beaker for beaker2: "))

indices = {
    "leftc": leftc,
    "watc": watc,
    "goalc": goalc,
    "beak1c": beak1c,
    "beak2c": beak2c
}
# Načtení souboru s názvem "text"
with open("data/qr_results_new.txt", "r") as file:
    lines = file.readlines()


# Funkce pro získání souřadnic pro daný index
def get_coords(beaker_index, lines):
    for line in lines:
        parts = line.split()
        index = int(parts[0])
        if index == beaker_index:
            return (float(parts[1]), float(parts[2]))
    return None


coords_leftc = get_coords(leftc, lines)
coords_watc = get_coords(watc, lines)
coords_goalc = get_coords(goalc, lines)
coords_beak1c = get_coords(beak1c, lines)
coords_beak2c = get_coords(beak2c, lines)

for name, index in indices.items():
    coords = get_coords(index, lines)
    if coords:
        print(f"Coordinates for {name} (beaker {index}) are: ({coords[0]}, {coords[1]})")
    else:
        print(f"Beaker with index {index} ({name}) not found.")

'''

def index_coordinate_1():
    # Retrieving indexes from the user (the index is contained in the QR code)
    leftc = int(input("Write index of beaker for leftovers: "))
    watc = int(input("Write index of beaker for water: "))
    goalc = int(input("Write index of beaker for goal_beaker: "))
    beak1c = int(input("Write index of beaker for beaker1: "))
    beak2c = int(input("Write index of beaker for beaker2: "))

    indices = {
        "leftc": leftc,
        "watc": watc,
        "goalc": goalc,
        "beak1c": beak1c,
        "beak2c": beak2c
    }

    soubor = "data/qr_results_new.txt"
    # Načtení souboru
    with open(soubor, "r") as file:
        lines = file.readlines()

    # Funkce pro získání souřadnic pro daný index
    def get_coords(beaker_index, lines):
        for line in lines:
            parts = line.split()
            index = int(parts[0])
            if index == beaker_index:
                return (float(parts[1]), float(parts[2]))
        return None
    

    coords_leftc = get_coords(leftc, lines)
    coords_watc = get_coords(watc, lines)
    coords_goalc = get_coords(goalc, lines)
    coords_beak1c = get_coords(beak1c, lines)
    coords_beak2c = get_coords(beak2c, lines)

    for name, index in indices.items():
        coords = get_coords(index, lines)
        if coords:
            print(f"Coordinates for {name} (beaker {index}) are: ({coords[0]}, {coords[1]})")
        else:
            print(f"Beaker with index {index} ({name}) not found.")

    return coords_leftc, coords_watc, coords_goalc, coords_beak1c, coords_beak2c


coords_leftc, coords_watc, coords_goalc, coords_beak1c, coords_beak2c = index_coordinate_1()
print(coords_goalc)

'''
    # Získání souřadnic pro jednotlivé indexy
    coords_dict = {}
    for name, index in indices.items():
        coords = get_coords(index, lines)
        if coords:
            coords_dict[name] = coords
            print(f"Coordinates for {name} (beaker {index}) are: ({coords[0]}, {coords[1]})")
        else:
            coords_dict[name] = None
            print(f"Beaker with index {index} ({name}) not found.")
    
    return coords_dict

'''
