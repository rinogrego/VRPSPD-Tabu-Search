import lp
import numpy as np
from itertools import permutations, combinations

class Tabu_Search(lp.LP):
    def __init__(self, lp, N_iter=100, tabu_tenure=10):
        super().__init__(**lp.__dict__)
        self.tabu_tenure = tabu_tenure
        self.N_iter = N_iter
        self.best_solution = None
        self.initial_solution = None
        
    def get_tabu_structure(self):
        tabu_strucutre = {}
        pass
        
    def construct_edge_order(self, node_order):
        """Turns something like [0, 1, 2, 3, 4, 0] to [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
        """
        path_as_edge_order = []
        for idx in range(len(node_order)-1):
            edge = (node_order[idx], node_order[idx+1])
            path_as_edge_order.append(edge)
        return path_as_edge_order
    
    def construct_edge_matrix(self, path_as_edge_order):
        """Turns [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)] into adjacency matrix
        """
        vertices_num = len(self.graph.nodes)
        edges_matrix = np.zeros([vertices_num, vertices_num])
        for edge in path_as_edge_order:
            edges_matrix[edge] = 1
        return edges_matrix
        
    def get_initial_solution(self, perm_search=4):
        if self.initial_solution is not None:
            return self.initial_solution
        
        V_C = [node for node in self.graph.nodes if node != 0]
        all_possible_paths = [[0] + list(p) + [0] for p in permutations(V_C, min(len(V_C), perm_search))]
        
        for candidate_init_path in all_possible_paths:
            if not self.check_constraints(candidate_init_path):
                return candidate_init_path
            
        if perm_search < len(V_C):
            # keep searching by increasing the search space by adding the permutation number
            return self.get_initial_solution(self, perm_search=perm_search+1)
        else:
            return f"No possible solution found after P_r={perm_search}."
    
    def evaluate_objective_function(self, path):
        """Evaluate the objective function from a given path
        """
        path_as_edge_order = self.construct_edge_order(path)
        X = self.construct_edge_matrix(path_as_edge_order)
        C = self.cost
        return eval(self.objective_function)
    
    def construct_YZ_flow(self, path_as_edge_order):
        """Construct the flow of pickup and delivery between each nodes
        """
        vertices_num = len(self.graph.nodes)
        
        Y = np.zeros([vertices_num, vertices_num])
        pickup = 0
        for edge in path_as_edge_order:
            i = edge[0]
            j = edge[1]
            pickup += self.pickup[i]
            Y[i][j] = pickup
        assert pickup == sum(self.pickup) 
        
        Z = np.zeros([vertices_num, vertices_num])
        delivery = sum(self.delivery)
        for edge in path_as_edge_order:
            i = edge[0]
            j = edge[1]
            delivery -= self.delivery[i]
            Z[i][j] = delivery
        assert delivery == 0
        
        return Y, Z
    
    def check_constraints(self, path):
        """Check the potential solution path against the constraints
        Parameters
        ----------
        path : List
        list of edges that corresponds a path
        Returns
        ----------
        bool
        indicates whether the constraints are violated or not
        """
        path_as_edge_order = self.construct_edge_order(path)
        X = self.construct_edge_matrix(path_as_edge_order)
        C = self.cost
        P = self.pickup
        D = self.delivery
        Q = self.capacity
        Y, Z = self.construct_YZ_flow(path_as_edge_order)
        print("Matriks flow Y:")
        print(Y)
        print("Matriks flow Z:")
        print(Z)
        print("Matriks flow Y + Z:")
        print(Y + Z)

        for constraint in self.constraints:
            # print(constraint)
            if eval(constraint) == False:
                print("The following constraint is violated:\n", constraint)
                return False
        return True
    
    def get_solution_neighborhood(self, path):
        """Get neighborhood of possible solutions of current solution
        """
        path_neighborhood = []
        # node swap
        non_depot_nodes = path[1:-1]
        for node_1, node_2 in combinations(non_depot_nodes, 2):
            _non_depot_nodes = non_depot_nodes.copy()
            i = _non_depot_nodes.index(node_1)
            j = _non_depot_nodes.index(node_2)
            _non_depot_nodes[i], _non_depot_nodes[j] = _non_depot_nodes[j], _non_depot_nodes[i]
            path_neighborhood.append([0] + _non_depot_nodes + [0])
        return path_neighborhood
    
    def run_brute(self):
        print("="*100)
        print("BRUTE FORCE SEARCH START\n")
        V_C = [node for node in self.graph.nodes if node != 0]
        all_possible_paths = [[0] + list(p) + [0] for p in permutations(V_C, len(V_C))]
        
        init_path = self.get_initial_solution() # returns: [0, 1, 3, 2, 0]
        
        current_best_path = init_path
        current_best_val = self.evaluate_objective_function(current_best_path)
        
        print("Initial solution:", current_best_path)
        print("Initial value:", current_best_val)
        print()
        
        #Brute force all possible paths
        for path in all_possible_paths:
            print("Checking path:", path)
            val = self.evaluate_objective_function(path)
            print("Value:", val)
            if not self.check_constraints(path):
                print("Constraints violated!")
                print()
                continue
            print("Constraints not violated, solution is feasible!")
            print(f"Compare: {val} < {current_best_val}")
            if val < current_best_val:
                print("Current value is better, this solution is currently the best!")
                current_best_path = path
                current_best_val = self.evaluate_objective_function(current_best_path)
            else:
                print(f"Currently checked value is not better than before. The path {path} is not chosen")
            print()

        self.best_solution = current_best_path
        print("BRUTE FORCE SEARCH FINISHED")
        print("="*100)
    
    def run(self):
        print("="*100)
        print("TABU SEARCH START\n")
        
        init_path = self.get_initial_solution() # returns: [0, 1, 3, 2, 0]
        
        current_best_path = init_path
        current_best_val = self.evaluate_objective_function(current_best_path)
        
        print("Initial solution:", current_best_path)
        print("Initial value:", current_best_val)
        print()
        
        i = 0
        while i < self.N_iter:
            i += 1
            print(f"{'Iteration': <30}:", i)
            print(f"{'Current best path': <30}:", current_best_path)
            # get neighborhood solution of current solution as new candidate solutions
            path_neighborhood = self.get_solution_neighborhood(current_best_path)
            
            # check the objective value of each candidate solution
            for candidate_path in path_neighborhood:
                print("Checking path:", candidate_path)
                candidate_val = self.evaluate_objective_function(candidate_path)
                print("Value:", candidate_val)
                if not self.check_constraints(candidate_path):
                    print("Constraints violated!")
                    print()
                    continue
                print("Constraints are not violated. Candidate solution is feasible!")
                
                print(f"Compare: {candidate_val} < {current_best_val}")
                if candidate_val < current_best_val:
                    print("Current value is better, this solution is currently the best!")
                    current_best_path = candidate_path
                    current_best_val = self.evaluate_objective_function(current_best_path)
                else:
                    print(f"Currently checked value is not better than before. The path {candidate_path} is not chosen")
                    # aspiration criteria
                    
                print()

            # intensification
            
            # diversification
        
        self.best_solution = current_best_path
        print("TABU SEARCH FINISHED")
        print("="*100)
    
    def get_best_solution(self):
        return self.best_solution
    
    def get_best_value(self):
        return self.evaluate_objective_function(self.best_solution)
    
    def __str__(self):
        return "\nTabu Search Registered."
    

if __name__ == "__main__":
    lp = lp.construct_problem()
    
    ts_brute = Tabu_Search(lp)
    ts_brute.run_brute()
    
    ts = Tabu_Search(lp, N_iter=5)
    ts.run()
    
    print("Best solution (brute force)")
    print("Path:", ts_brute.get_best_solution())
    print("Value:", ts_brute.get_best_value())
    
    print("Best solution (tabu search)")
    print("Path:", ts.get_best_solution())
    print("Value:", ts.get_best_value())