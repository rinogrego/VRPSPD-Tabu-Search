import numpy as np
import networkx as nx

COST = np.array([
    [ 0, 25, 15, 10],
    [25,  0,  5, 30],
    [15,  5,  0, 20],
    [10, 30, 20,  0],
])
G = nx.from_numpy_array(COST, create_using=nx.DiGraph)
V = G.nodes
V_C = [node for node in G.nodes if node != 0]
PICKUP = np.array([0, 30, 60, 20])
DELIVERY = np.array([0, 70, 10, 40])
CAPACITY = 150

for node, (pickup_val, delivery_val) in enumerate(zip(PICKUP, DELIVERY)):
    G.nodes[node]["pickup"] = pickup_val
    G.nodes[node]["delivery"] = delivery_val

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