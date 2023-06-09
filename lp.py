import data

class LP(object):
    def __init__(self, graph, cost, objective_function, constraints, pickup, delivery, capacity):
        self.graph = graph
        self.cost = cost
        self.objective_function = objective_function
        self.constraints = constraints
        self.pickup = pickup
        self.delivery = delivery
        self.capacity = capacity
        
    def __str__(self):
        constraints_string = "\n".join(["{0}   (Eq. {1})".format(f"{const: >150}", f"{idx+1}".zfill(3)) for idx, const in enumerate(self.constraints)])
        _info = {
            "Capacity     (Q)": self.capacity,
            "Pickup       (P)": self.pickup,
            "Delivery     (D)": self.delivery,
        }
        infos = "\n".join([f"{key}: {value}" for key, value in _info.items()])
        return "\nFollowing LP problem has been registered:\n\nMINIMIZE:\n\n{0}\n\nSubject to:\n\n{1}\n\nWith:\n\n{2}\nMatriks Cost (X):\n{3}".format(self.objective_function, constraints_string, infos, self.cost)


def construct_problem():
    
    G, COST, OBJ_FUNC, CONSTRAINTS, PICKUP, DELIVERY, CAPACITY = data.get(instance="instance_two")
                
    lp = LP(
        graph=G,
        cost=COST,
        objective_function=OBJ_FUNC,
        constraints=CONSTRAINTS,
        pickup=PICKUP,
        delivery=DELIVERY,
        capacity=CAPACITY
    )
    
    print(lp)
    
    return lp