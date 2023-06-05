import lp
import numpy as np
from itertools import permutations, combinations

import os
import sys
from datetime import datetime
import pprint
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--log', type=str, help='Specify log filepath for output. Input "cmd" to to display on the command line. Otherwise new file will be automatically created.')
args = parser.parse_args()
log_to_cmd = False
if args.log is not None:
    if args.log.lower() == 'cmd':
        log_to_cmd = True


class Tabu_Search(lp.LP):
    def __init__(self, lp, N_iter=10, tabu_tenure=5, penalty_value=5, initial_solution=None):
        super().__init__(**lp.__dict__)
        self.tabu_tenure = tabu_tenure
        self.N_iter = N_iter
        self.penalty_value = penalty_value
        self.initial_solution = initial_solution
        self.best_solution = None
        
    def get_tabu_structure(self):
        tabu_structure = {}
        V_C = [node for node in self.graph.nodes if node != 0]
        for swap in combinations(V_C, 2):
            tabu_structure[swap] = {
                "tabu_time": 0,
                "move_value": 0,
                "freq": 0,
                "penalty": 0
            }
            
        return tabu_structure
        
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
            if self.check_constraints(self.initial_solution):
                return self.initial_solution
            else:
                print("Given initial solution {0} violates constraints.".format(self.initial_solution))
                print("New initial solution will be searched.")

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
        # print("Matriks flow Y:")
        # print(Y)
        # print("Matriks flow Z:")
        # print(Z)
        # print("Matriks flow Y + Z:")
        # print(Y + Z)

        for constraint in self.constraints:
            # print(constraint)
            if eval(constraint) == False:
                print("The path {0} violates the following constraint:\n{1}\n".format(path, constraint))
                return False
        return True
    
    def swap_move(self, path, node_i, node_j):
        '''Takes a list (solution)
        returns a new neighbor solution with i, j swapped
       '''
        path = path.copy()
        # job index in the solution:
        i_index = path.index(node_i)
        j_index = path.index(node_j)
        #Swap
        path[i_index], path[j_index] = path[j_index], path[i_index]
        return path
    
    def run_brute(self):
        print("="*100)
        print("BRUTE FORCE SEARCH START\n")
        V_C = [node for node in self.graph.nodes if node != 0]
        all_possible_paths = [[0] + list(p) + [0] for p in permutations(V_C, len(V_C))]
        
        init_path = self.get_initial_solution()
        
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
        
        current_path = init_path
        current_value = self.evaluate_objective_function(current_path)
        best_path = init_path
        best_value = self.evaluate_objective_function(best_path)
        tabu_structure = self.get_tabu_structure()
        tenure = self.tabu_tenure
        # iteration to keep track of tabu tenure. instead of reducing the value
        # of tabu tenure of every swap in every iteration, just increase the
        # iteration and tabu tenure is tracked by the time took to reach 
        # the particular swap
        i = 1
        # iteration for termination if no better solution is found
        i_termination = 0
        
        print("Initial solution:", best_path)
        print("Initial value:", best_value)
        print()
        
        while i_termination < self.N_iter:
            
            # process through all possible swaps as neighborhood of current solution
            for move in tabu_structure.keys():
                candidate_path = self.swap_move(best_path, move[0], move[1])
                candidate_path_value = self.evaluate_objective_function(candidate_path)
                tabu_structure[move]["move_value"] = candidate_path_value
                tabu_structure[move]["penalty"] = candidate_path_value + (tabu_structure[move]["freq"] * self.penalty_value)
                    
            # find admissible move by intensification phase
                
            # find admissible move by diversification phase
            while True:
                print()
                print(f"{'Current_best_path': <20}:", best_path)
                print(f"{'Current_best_value': <20}:", best_value)
                print("Tabu Structure:")
                pprint.pprint(tabu_structure)
                # select the move with the lowest penalized value
                best_move = min(tabu_structure, key=lambda x: tabu_structure[x]["penalty"])
                
                if tabu_structure[best_move]["penalty"] == np.inf:
                    print(f"{'status': <20}: All available moves are Tabu and Inadmissible")
                    i_termination += 1
                    break
                    
                move_value = tabu_structure[best_move]["move_value"]
                tabu_time = tabu_structure[best_move]["tabu_time"]
                print(f"{'best_move': <20}:", best_move)
                print(f"{'move_value': <20}:", move_value)
                print(f"{'best_move_penalty': <20}:", tabu_structure[best_move]["penalty"])
                print(f"{'i_termination': <20}:", i_termination)
                print(f"{'iteration': <20}:", i)
                # if the least penalized move not tabu
                if tabu_time < i:
                    # make the move
                    current_path = self.swap_move(current_path, best_move[0], best_move[1])
                    current_value = self.evaluate_objective_function(current_path)
                    # least penalized move is a better move
                    if move_value < best_value:
                        # least penalized move don't violate constraints
                        if self.check_constraints(current_path):
                            best_path = current_path
                            best_value = current_value
                            print(f"{'status': <20}: Best Improving => Admissible")
                            i_termination = 0
                        # least penalized move violates constraints
                        else:
                            print(f"{'status': <20}: Best Improving => Infeasible")
                            i_termination += 1
                    # least penalized move is not a better move
                    else:
                        print(f"{'status': <20}: Least non-Improving => Admissible")
                        i_termination += 1
                    # update tabu_time and frequency of swap
                    tabu_structure[best_move]["tabu_time"] = i + tenure
                    tabu_structure[best_move]["freq"] += 1
                    i += 1
                    break
                # if the move is tabu
                else:
                    # Aspiration criteria
                    # tabu move have better value
                    if move_value < best_value:
                        # tabu move don't violate constraints
                        if self.check_constraints(current_path):
                            current_path = self.swap_move(current_path, best_move[0], best_move[1])
                            current_value = self.evaluate_objective_function(current_path)
                            best_path = current_path
                            best_value = current_value
                            tabu_structure[best_move]['freq'] += 1
                            i_termination = 0 
                            i += 1
                            print(f"{'status': <20}: Aspiration => Admissible")
                            break
                        # tabu move violates constraints
                        else:
                            tabu_structure[best_move]['penalty'] = np.inf
                            print(f"{'status': <20}: Aspiration => Infeasible")
                            # continue searching better move
                            continue
                    # tabu move is not even better
                    else:
                        tabu_structure[best_move]['penalty'] = np.inf
                        print(f"{'status': <20}: Tabu => Inadmissible")
                        # continue searching better move
                        continue
            print("\nIteration {0} have been reached without finding the next best solution\n".format(self.N_iter))
        
        self.best_solution = best_path
        print("\nTABU SEARCH FINISHED")
        print(f"{'best_path': <20}:", best_path)
        print(f"{'best_value': <20}:", best_value)
        print(f"{'i_termination': <20}:", i_termination)
        print(f"{'iteration': <20}:", i)
        print("="*100)
    
    def get_best_solution(self):
        return self.best_solution
    
    def get_best_value(self):
        return self.evaluate_objective_function(self.best_solution)
    
    def __str__(self):
        return "\nTabu Search Registered."
    

if __name__ == "__main__":
    
    log_folder = os.path.join(os.getcwd(), "log")
    LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}_Log-TS.log"
    os.makedirs(log_folder, exist_ok=True)
    if log_to_cmd:
        LOG_FILE_PATH = None
    else:
        LOG_FILE_PATH = os.path.join(log_folder, LOG_FILE)
    
    if LOG_FILE_PATH is not None:
        original_stdout = sys.stdout
        f = open(LOG_FILE_PATH, "a")
        sys.stdout = f
    
    lp = lp.construct_problem()
    initial_solution = [0, 1, 2, 3, 4, 0]
    penalty_value = 10000
    # initial_solution = None
    
    ts_brute = Tabu_Search(lp, initial_solution=initial_solution, penalty_value=penalty_value)
    ts_brute.run_brute()
    
    ts = Tabu_Search(lp, N_iter=10, initial_solution=initial_solution, penalty_value=penalty_value)
    ts.run()
    
    print("Best solution (brute force)")
    print("Path:", ts_brute.get_best_solution())
    print("Value:", ts_brute.get_best_value())
    print()
    print("Best solution (tabu search)")
    print("Path:", ts.get_best_solution())
    print("Value:", ts.get_best_value())
    
    if LOG_FILE_PATH is not None:
        sys.stdout = original_stdout