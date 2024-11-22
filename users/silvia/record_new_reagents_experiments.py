import sys
import numpy as np
from experiments_new_reagents import NewReagentsExperiments
from petri_dish_coordinates import petridishes
import os

experiment = NewReagentsExperiments()

individual_number = 1

reagents = ['PEG', 'TRITONX', 'DECANOATE']


def do_stuff_here(petri, gen, reagent_name):
    """This function prepares the liquid mix with ph and molarity from the individual """
    global individual_number
    print "Preparing experiment"
    os.system("say 'Preparing experiment'")
    experiment.prepare_experiment(petri, reagent_name)
    print "Experiment prepared, starting experiment"
    os.system("say 'Experiment prepared, starting experiment'")

    petri.clean_flag = False

    fitness = experiment.perform_experiment(petri, gen, individual_number, reagent_name, replica_num=0)
    individual_number += 1

    print "Experiment has finished"
    os.system("say 'Experiment has finished'")

    print "Check that all the vessels have enough reagents!"
    os.system("say 'Check that all the vessels have enough reagents!'")

    return fitness


def launch_experiments(reagent):
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

    fitness = do_stuff_here(petri, gen, reagent)
    return fitness


reagent_number = 2  # 0, 1, 2 # SCRIVERE QUA QUALE REAGENTE PRENDERE

if __name__ == '__main__':
    os.system("say 'Performing experiments with %s'" % (reagents[reagent_number]))
    for i in range(0, 8):
        launch_experiments(reagents[reagent_number])


