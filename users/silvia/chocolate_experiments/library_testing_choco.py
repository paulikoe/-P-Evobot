import chocolate as choco

import matplotlib.pyplot as plt
import seaborn as sns; sns.set()

import numpy as np
import pandas as pd


def himmelblau(x, y):
    return (x ** 2 + y - 11) ** 2 + (x + y ** 2 - 7) ** 2


def function_to_evaluate(x, y):
    # x, y = individual[0], individual[1]
    fitness = x ** 2 + y ** 2
    return fitness


space = choco.Space({"x": choco.quantized_uniform(0, 7, 2),
                     "y": choco.quantized_uniform(0, 7, 2)})

# for key, value in space.iteritems():
#     print key, value


# establish where the results should be saved

conn = choco.SQLiteConnection("sqlite:///chocolate_2.db")

cv = choco.Repeat(repetitions=3, rep_col="_repetition_id", reduce=np.mean)

sampler = choco.QuasiRandom(conn, space, crossvalidation=cv, clear_db=True)

token, params = sampler.next()  # token is a unique id to trace parameters in the database

loss = function_to_evaluate(**params)

print(token, params, loss)

sampler.update(token, loss)

results = conn.results_as_dataframe()

print results

results = pd.melt(results, id_vars=["_loss"], value_name='value', var_name="variable")

sns.lmplot(x="value", y="_loss", data=results, col="variable", sharex=False)

plt.show()
