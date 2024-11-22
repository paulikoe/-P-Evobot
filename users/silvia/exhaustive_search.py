import sys

import numpy as np

from recording_experiments import RecordingExperiment
from petri_dish_coordinates import petridishes

import os

phes = np.linspace(0, 1, 6)
molarities = np.linspace(0, 1, 4)

experiment = RecordingExperiment()

individual_number = 0


def do_stuff_here(petri, individual, gen):

    """This function prepares the liquid mix with ph and molarity from the individual """
    global individual_number
    print "Preparing experiment"
    os.system("say 'Preparing experiment'")
    ph, molarity = experiment.prepare_experiment(individual, petri)
    print "Experiment prepared, starting experiment"
    os.system("say 'Experiment prepared, starting experiment'")

    petri.clean_flag = False

    fitness = experiment.perform_experiment(petri, ph, molarity, gen, individual_number, replica_num=0)
    individual_number += 1

    print "Experiment has finished"
    os.system("say 'Experiment has finished'")

    print "Check that all the vessels have enough reagents!"
    os.system("say 'Check that all the vessels have enough reagents!'")

    return fitness


def eval_max(individual):
    """This function perform the experiment (add decanol and salt), performs the tracking and evaluate the fitness
    value """
    gen = 0
    for p in petridishes:
        if p.is_clean():
            petri = p
            break
    else:
        # We did not find any clean petri dish
        repeat = True
        while repeat:
            print "There are no clean petri dishes"
            os.system("say 'There are no clean petri dishes'")
            print "Check that all the vessels have enough reagents and place clean petri dishes!"
            os.system("say 'Check that all the vessels have enough reagents and place clean petri dishes!'")

            print "Is everything OK? Type ""y"" to continue"
            text = sys.stdin.readline()
            if "y" in text:
                repeat = False
        # Take the firs petri dish (all are clean now)
        for petris in petridishes:
            petris.clean_flag = True
        petri = petridishes[0]

    fitness = do_stuff_here(petri, individual, gen)
    return fitness

ph = 0.0
molarity = 0.0

ph2 = 0.8
molarity2 = 0.0
for i in range(0, 17):
    eval_max((ph, molarity))


# for mol in molarities:
#     for phh in phes:
#         eval_max((phh, mol))
