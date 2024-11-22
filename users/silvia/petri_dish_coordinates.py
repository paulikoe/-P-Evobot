# Coordinates of the Petri dishes on the experimental layer
import sys
from petridish import PetriDish
sys.path.append('../api')
sys.path.append('../settings')


# coordinates of the petri dishes centers with syringe in socket 4 - decanol

petri_dish_coord = {0: (195, 165),
                    1: (195, 261),
                    2: (195, 356),
                    3: (195, 454),
                    4: (97, 165),
                    5: (97, 261),
                    6: (97, 356),
                    7: (97, 454),
                    "waste": (17, 424),
                    "clean_water": (17, 580)
                    }

# coordinates of the petri dishes centers with syringe in socket 9 - decanol
#
# petri_dish_coord = {0: (193, 183),
#                     1: (193, 279),
#                     2: (193, 380),
#                     3: (193, 478),
#                     4: (97, 183),
#                     5: (97, 279),
#                     6: (97, 380),
#                     7: (97, 478),
#                     # 'waste': (23, 415),
#                     # 'clean_water': (23, 499),
#                     "waste": (23, 499),
#                     "clean_water": (23, 580)
#                     }


goalPos = -40
diameter = 90
cleanliness = True
evobot = None
# the petridishes are instantiated with the cleanliness flag set to True, same diameter and coordinates from the dict
petridishes = []
for i in range(len(petri_dish_coord)-2):
    petridishes.append(PetriDish(evobot, petri_dish_coord[i], goalPos, diameter, cleanliness, worldCor=None))

# toilet_petri = PetriDish(evobot, petri_dish_coord['toilet'], goalPos, diameter, worldCor=worldcor)





