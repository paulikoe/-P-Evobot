import datetime
import pickle
import random
import sys

import numpy as np
from deap import base

from deap import cma
from deap import creator
from deap import tools

from evol_experiment_third_fitness import EvolutionaryExperimentThirdFitness

from petri_dish_coordinates import petridishes

import os

sys.path.append('../../api')
sys.path.append('../../settings')

IND_SIZE = 2
NGEN = 5  # number of generations for which the evolution runs
number_children = 8  # number of individuals in each population - 8 individuals

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
creator.create("Strategy", list)

random.seed(datetime.datetime.now().microsecond)
np.random.seed(datetime.datetime.now().microsecond)

toolbox = base.Toolbox()
toolbox.register("attribute", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=IND_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


stats = tools.Statistics(lambda individual: individual.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)


experiment = EvolutionaryExperimentThirdFitness()
individual_number = 0


# def resetIndividualNumber():
#     global_individual_number = 0.0

fake_experiment = False


def do_stuff_here(petri, individual, gen, individual_num, replica_num):
    """This function prepares the liquid mix with ph and molarity from the individual """
    print "Preparing experiment"
    os.system("say 'Preparing experiment'")
    ph, molarity = experiment.prepare_experiment(individual, petri)
    print "Experiment prepared, starting experiment"
    os.system("say 'Experiment prepared, starting experiment'")
    fitness = experiment.perform_experiment(petri, ph, molarity, gen, individual_num, replica_num)
    petri.clean_flag = False
    print "Experiment has finished"
    os.system("say 'Experiment has finished'")
    print "Check that all the vessels have enough reagents!"
    os.system("say 'Check that all the vessels have enough reagents!'")

    return fitness


def eval_max(individual, gen):
    """"This function perform the experiment (add decanol and salt), performs the tracking and evaluate the fitness 
    value """
    global individual_number
    fitness = []
    num_replication = 4
    for replica_num in range(0, num_replication):
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
        if not fake_experiment:
            # TODO add comment here
            fitness.append(do_stuff_here(petri, individual, gen, individual_number, replica_num))
        else:
            print gen, individual_number, replica_num
    individual_number += 1
    return np.median(fitness)


toolbox.register("evaluate", eval_max)


def check_individuals(individual):
    """ This function checks if the individual's attributes are in the boundaries: if x or y < 0 -> 0 if x or y > 1 
    -> 1 """
    x, y = individual[0], individual[1]
    # print 'old x %f' % x
    # print 'old y %f' % y
    if x < 0.:
        new_x = 0.
        individual[0] = new_x
        # print 'new x %d' % new_x
        # print 'same y %f' % y
    elif x > 1.:
        new_x_1 = 1.
        individual[0] = new_x_1
    if y < 0.:
        new_y = 0.
        individual[1] = new_y
        # print 'new y %d' % new_y
        # print 'same x %f' % x
    elif y > 1.:
        new_y_1 = 1.
        individual[1] = new_y_1

    return individual


def main(population_file="population-g2.pkl"):
    global individual_number
    print "The evolutionary experiments start now!"
    os.system("say 'Good afternoon Carlotta! Is everything ready ?'")
    os.system("say 'The evolutionary experiments start now!'")
    if not population_file:
        # create an initial population of individuals (where each individual is a list of floats)
        strategy = cma.Strategy(centroid=[0.5] * IND_SIZE, sigma=0.15, lambda_=number_children)
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)
        start_gen = 0
        population = []
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
        hall_of_fame = tools.HallOfFame(1)

    else:
        cp = pickle.load(open(population_file, "r"))
        population = cp["population"]
        start_gen = cp["generation"] + 1
        random.setstate(cp["rndstate"])
        np.random.set_state(cp["numpy_rndstate"])
        fitnesses = cp["fitness"]
        hall_of_fame = cp["halloffame"]
        logbook = cp["logbook"]
        strategy = cp["strat"]
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)

        # for ind, fit in zip(population, fitnesses):
        #     ind.fitness.values = fit,

        print("Start of evolution")

    for gen in range(start_gen, NGEN):
            print("-- Generation %i --" % gen)
            os.system('say "Generation %i"' % gen)

            # Generate a new population
            population = toolbox.generate()

            for ind in population:
                check_individuals(ind)  # check the attributes of each individual

            # Evaluate the individuals
            fitnesses = toolbox.map(toolbox.evaluate, population, [gen]*len(population))
            print 'GENERATION: %d' % gen
            print 'POPULATION: %s' % population
            print 'FITNESSES: %s' % fitnesses

            individual_number = 0
            # resetIndividualNumber()

            for ind, fit in zip(population, fitnesses):
                ind.fitness.values = fit,
                hall_of_fame.update(population)

            # Update the strategy with the evaluated individuals
            toolbox.update(population)

            record = stats.compile(population) if stats is not None else {}
            logbook.record(gen=gen, nevals=len(population), **record)
            print logbook

            import csv
            my_list = zip(population, fitnesses)
            print my_list
            with open('/Users/capo/Documents/data_from_exp/logbook/generation_summary-{}.csv'.format(
                    datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")), 'wb') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(['generation %d ' % gen])
                writer.writerows([
                    my_list
                ])

            cp = dict(population=population, generation=gen, fitness=fitnesses, rndstate=random.getstate(),
                      strat=strategy,
                      halloffame=hall_of_fame,
                      logbook=logbook,
                      numpy_rndstate=np.random.get_state())
            filename = "population-g" + str(gen) + ".pkl"
            pickle.dump(cp, open(filename, "wb"))

    print "-- End of (successful) evolution --"

    best_ind = tools.selBest(population, 1)[0]
    print "Best individual is %s, %s" % (best_ind, best_ind.fitness.values)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
