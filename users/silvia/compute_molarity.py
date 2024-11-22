import sys



# molarities = [5, 10, 15, 20]
# phes = [7, 8, 9, 10, 11, 12]

import numpy as np

phes = np.linspace(0, 1, 6)

molarities = np.linspace(0, 1, 4)

for mol in molarities:
    for phh in phes:
        print phh, mol
        # ph_real = 7.0 + ((12.3 - 7.0) * phh)  # give me a number between 7 and 12.3 with decimals
        ph_real = 7 + (5 * phh)  # give me a number between 7 and 12 with decimals - changed for exhaustive search
        mol_real = 5.0 + ((20.0 - 5.0) * mol)  # give me a number between 5 and 20
        print ph_real, mol_real


for i in range(0,9):
    print i