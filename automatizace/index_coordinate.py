# prirazeni_zadaneho_indexu_ke_kadince_finale

def index_coordinates(assignment,indices_from_gui):
    # Determine required beakers based on assignment
    required_beakers = None

    if assignment == 1:
        required_beakers = ["leftovers", "water", "goal beaker", "beaker1", "beaker2"]
    elif assignment == 2:
        required_beakers = ["leftovers", "water", "beaker1", "goal beaker"]
    if required_beakers is None:
        raise ValueError("Invalid assignment value.")
    indices = {}
    
    
    '''
    # Retrieve indexes for each required beaker
    for beaker in required_beakers:
        indices[beaker] = int(input(f"Write index of beaker for {beaker}: "))
    '''
    for beaker in required_beakers:
        if beaker in indices_from_gui:
            indices[beaker] = int(indices_from_gui[beaker])  # Předpokládáme, že indices_from_gui jsou hodnoty z GUI
        else:
            raise ValueError(f"Missing index for {beaker}")
        
    # Retrieve coordinates from the file based on the indices
    lines = linesF()
    coordinates = {beaker: get_coords(index, lines) for beaker, index in indices.items()}
    
    with open("data/coord_try.txt", 'w') as file:
        for beaker, coord in coordinates.items():
            file.write(f"{beaker}: {coord}\n")

    return coordinates


def get_coords(beaker_index, lines):
    for line in lines:
        parts = line.split()
        index = int(parts[0])
        if index == beaker_index: # pokud se index z QR kodu = indexu od uzivatele - priradi se to
            return float(parts[1]), float(parts[2])
    return None


def linesF():
    with open("data/qr_results_new.txt", "r") as file:
        return file.readlines()







