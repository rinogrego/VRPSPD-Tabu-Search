from . import instance_one, instance_two, create_instance

def get(instance: str, seed=None):
    if instance == "instance_one":
        _instance = instance_one
    elif instance == "instance_two":
        _instance = instance_two
    elif instance == "create_instance":
        if seed is not None and type(seed) == int:
            _instance = create_instance(seed=seed)
            _instance.create()
        else:
            _instance = create_instance()
            _instance.create()
    else:
        return "No instance found"
            
    G = _instance.G
    COST_TEST = _instance.COST_TEST
    OBJ_FUNC = _instance.OBJ_FUNC
    CONSTRAINTS = _instance.CONSTRAINTS
    PICKUP = _instance.PICKUP
    DELIVERY = _instance.DELIVERY
    CAPACITY = _instance.CAPACITY
    
    return G, COST_TEST, OBJ_FUNC, CONSTRAINTS, PICKUP, DELIVERY, CAPACITY