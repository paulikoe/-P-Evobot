import array, random, math
from deap import creator, base, tools, algorithms


def evalFitness(alc):
    out = 0
    for bit in alc:
        out = (out << 1) | bit    
    alcVol=out/math.pow(2, len(alc))
    print "alcVol:", alcVol

    #to be implemented
    #syringe1.fillVolFrom( head, ml=alcVol, container=alcPetridish )
    cocktailFitness = raw_input("How do you like your drink from 1-10 ? ")
    print "cocktailFitness:",cocktailFitness  
    return cocktailFitness    



creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 100)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

evalTaste = lambda individual: (evalFitness(individual),)

toolbox.register("evaluate", evalTaste)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

population = toolbox.population(n=300)

NGEN=400
for gen in range(NGEN):
    offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
    fits = toolbox.map(toolbox.evaluate, offspring)
    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
    population = offspring
