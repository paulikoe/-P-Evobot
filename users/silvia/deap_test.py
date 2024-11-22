import numpy as np
import random
from deap import base
from deap import cma
from deap import creator
from deap import tools
import pickle
import datetime
import sys


def eval_max(individual):
    x, y = individual[0], individual[1]
    fitness = x ** 2 + y ** 2
    return fitness,


IND_SIZE = 2
NGEN = 10
number_children = 8
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
creator.create("Strategy", list)

random.seed(datetime.datetime.now().microsecond)
np.random.seed(datetime.datetime.now().microsecond)

toolbox = base.Toolbox()
toolbox.register("attribute", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=IND_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", eval_max)


stats = tools.Statistics(lambda individual: individual.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)


def check_individuals(individual):
    """ This function checks if the individual's attributes are in the boundaries: if x or y < 0 -> 0 if x or y > 1 
    -> 1 """
    x, y = individual[0], individual[1]
    if x < 0.:
        new_x = 0.
        individual[0] = new_x
    elif x > 1.:
        new_x_1 = 1.
        individual[0] = new_x_1
    if y < 0.:
        new_y = 0.
        individual[1] = new_y
    elif y > 1.:
        new_y_1 = 1.
        individual[1] = new_y_1

    return individual


def main(population_file=None):

    print "The evolutionary experiments start now!"
    if not population_file:
        # create an initial population of individuals (where each individual is a list of floats)
        strategy = cma.Strategy(centroid=[0.5] * IND_SIZE, sigma=0.15, lambda_=number_children)
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)
        start_gen = 0
        population = []
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
        halloffame = tools.HallOfFame(1)

    else:
        cp = pickle.load(open(population_file, "r"))
        population = cp["population"]
        start_gen = cp["generation"]+1
        random.setstate(cp["rndstate"])
        np.random.set_state(cp["numpy_rndstate"])
        fitnesses = cp["fitness"]
        halloffame = cp["halloffame"]
        logbook = cp["logbook"]
        strategy = cp["strat"]
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)

        # for ind, fit in zip(population, fitnesses):
        #     ind.fitness.values = fit,

        print("Start of evolution")

    for gen in range(start_gen, NGEN):

        print 'THIS IS THE PRIOR POPULATION %s: ' \
              % population

        # Generate a new population
        population = toolbox.generate()

        for ind in population:
            check_individuals(ind)

        # Evaluate the individuals
        fitnesses = toolbox.map(toolbox.evaluate, population)
        print 'GENERATION: %d' % gen
        print 'POPULATION: %s' % population
        print 'FITNESSES: %s' % fitnesses

        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
            halloffame.update(population)
        # Update the strategy with the evaluated individuals
        toolbox.update(population)

        record = stats.compile(population) if stats is not None else {}
        print record
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

        cp = dict(population=population, generation=gen, fitness=fitnesses, rndstate=random.getstate(), strat=strategy,
                  halloffame=halloffame,
                  logbook=logbook,
                  numpy_rndstate=np.random.get_state()
                  )
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
