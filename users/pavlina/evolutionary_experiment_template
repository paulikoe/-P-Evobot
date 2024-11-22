import datetime
import pickle
import random
import sys
import math
import numpy as np
from deap import base

from deap import cma
from deap import creator
from deap import tools
from MFCsEvolutionaryExperiment import MFCsEvolutionaryExperiment


sys.path.append('../../api')
sys.path.append('../../settings')

NUM_REPLICA = 3 # number of replica
NUM_MFC = 9 # number of mfc that we have for the experiment
IND_SIZE = 3 # the number of variables of the experiment
NGEN = 15  # number of generations for which the evolution runs
NUM_IND = int(math.floor(NUM_MFC/NUM_REPLICA))  # number of individuals in each population

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
creator.create("Strategy", list)

#Initialise the random number generators
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


experiment = MFCsEvolutionaryExperiment(NUM_REPLICA)
individual_number = 0






def check_individuals(individual):
    """ This function checks if the individual's attributes are in the boundaries [0,1] and that the sum of
    all the elements is 1.
    """

    # Remove negative numbers
    for i in range(len(individual)):
        if individual[i] < 0.0:
            individual[i] = 0.0

    sum = 0
    for i in range(len(individual)):
        sum += individual[i]

    for i in range(len(individual)):
        individual[i]  /= sum

    return individual


def main(population_file=None):
    global individual_number
    print "The evolutionary experiments start now!"

    if not population_file:
        # create an initial population of individuals (where each individual is a list of floats)
        strategy = cma.Strategy(centroid=[0.5] * IND_SIZE, sigma=0.2, lambda_= NUM_IND)
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)
        start_gen = 0
        population = []
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
        hall_of_fame = tools.HallOfFame(1)

    else:
        # There is a population file, resume the evolutionary experiment from the last generation
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

    # Main loop of the experiment
    for gen in range(start_gen, NGEN):
            print("-- Generation %i --" % gen)

            # Generate a new population
            population = toolbox.generate()

            for ind in population:
                check_individuals(ind)  # check the attributes of each individual

            # Evaluate the individuals

            #First, feed the MFCs with the recipes
            experiment.feed_MFCs(population, gen)


            #Wait some time

            #Evaluate the recipes
            fitnesses = experiment.evaluate_MFCs(population, gen)

            print 'GENERATION: %d' % gen
            print 'POPULATION: %s' % population
            print 'FITNESSES: %s' % fitnesses

            individual_number = 0

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
            with open('./exp_data/generation_summary-{}.csv'.format(
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
