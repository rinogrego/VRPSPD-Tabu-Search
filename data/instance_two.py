import numpy as np
import networkx as nx

COST = np.array([
    [     0, 70_000, 55_000,  3_000, 65_000],
    [70_000,      0, 14_000, 65_000, 75_000],
    [55_000, 14_000,      0, 50_000, 55_000],
    [ 3_000, 65_000, 50_000,      0, 65_000],
    [65_000, 75_000, 55_000, 65_000,      0],
])

G = nx.from_numpy_array(COST, create_using=nx.DiGraph)
V = G.nodes
V_C = [node for node in G.nodes if node != 0]
PICKUP = np.array([0, 17, 21, 35, 10])
DELIVERY = np.array([0, 16, 21, 35, 8])
# CAPACITY = max(sum(PICKUP), sum(DELIVERY))
CAPACITY = 150

for node, (pickup_val, delivery_val) in enumerate(zip(PICKUP, DELIVERY)):
  G.nodes[node]["pickup"] = pickup_val
  G.nodes[node]["delivery"] = delivery_val

# SINGLE_VEHICLE_CAPACITY = CAPACITY - np.sum([G.nodes[i]['delivery'] for i in V_C])
# SINGLE_VEHICLE_CUSTOMER_DEMAND = np.array([p-d for p, d in zip(PICKUP, DELIVERY)])

OBJ_FUNC = " + ".join([f"X[{i}][{j}]*C[{i}][{j}]" for i in G.nodes for j in G.nodes])

constraints_6_09 = [" + ".join([f"X[{i}][{j}]" for j in G.nodes]) + " == 1" for i in V_C]
constraints_6_10 = [" + ".join([f"X[{i}][{j}]" for j in G.nodes]) + " - " + " - ".join([f"X[{j}][{i}]" for j in G.nodes]) + " == 0" for i in G.nodes]
constraints_6_11 = [" + ".join([f"X[{0}][{i}]" for i in G.nodes]) + " <= 1"]
constraints_6_12 = [f"Y[{i}][{j}] + Z[{i}][{j}] <= Q * X[{i}][{j}]" for i in G.nodes for j in G.nodes]
constraints_6_13 = [" + ".join([f"Y[{i}][{j}]" for j in G.nodes]) + " - " + " - ".join([f"Y[{j}][{i}]" for j in G.nodes]) + f" == P[{i}]" for i in V_C]
constraints_6_14 = [" + ".join([f"Z[{j}][{i}]" for j in G.nodes]) + " - " + " - ".join([f"Z[{i}][{j}]" for j in G.nodes]) + f" == D[{i}]" for i in V_C]
constraints_6_15_Y = [f"Y[{i}][{j}]" + " >= 0" for i in G.nodes for j in G.nodes]
constraints_6_15_Z = [f"Z[{i}][{j}]" + " >= 0" for i in G.nodes for j in G.nodes]
constraints_6_SINGLE_VEHICLE = []
constraints_6_16 = [f"X[{i}][{j}]" + " in {0, 1}" for i in G.nodes for j in G.nodes]

CONSTRAINTS = constraints_6_09 +\
              constraints_6_10 +\
              constraints_6_11 +\
              constraints_6_12 +\
              constraints_6_13 +\
              constraints_6_14 +\
              constraints_6_15_Y +\
              constraints_6_15_Z +\
              constraints_6_16