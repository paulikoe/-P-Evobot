def load_coordinates_from_file():
    """Načte souřadnice z textového souboru a odstraní nechtěné znaky."""
    coordinates = {}
    with open("C:\Python\\afaina-evobliss-software-68090c0edb16\\automatizace\data\coord_try.txt", 'r') as file:
        lines = file.readlines()
        for line in lines:
            # Odstranění nechtěných znaků, jako jsou závorky nebo čárky
            clean_line = line.replace('(', '').replace(')', '').replace(',', '').strip()
            parts = clean_line.split()

            if len(parts) == 3:
                name, x, y = parts[0], float(parts[1]), float(parts[2])
                coordinates[name] = (x, y)
    return coordinates


# Použití funkce:
coordinates = load_coordinates_from_file()
print(coordinates)

