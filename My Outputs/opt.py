#!/usr/bin/env python
import argparse
import time
from itertools import combinations
from ortools.sat.python import cp_model

class ProgressCallback(cp_model.CpSolverSolutionCallback):
    """Callback to monitor solver progress and detect stalling."""
    def __init__(self, stall_threshold_s=600):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.start_time = time.time()
        self.last_solution_time = self.start_time
        self.solution_count = 0
        self.stall_threshold_s = stall_threshold_s

    def on_solution_callback(self):
        self.solution_count += 1
        current_time = time.time()
        self.last_solution_time = current_time
        elapsed = current_time - self.start_time
        print(f"[Progress] Solution {self.solution_count} found after {elapsed:.2f} seconds.")

    def check_stalling(self):
        current_time = time.time()
        if current_time - self.last_solution_time > self.stall_threshold_s:
            print(f"[Warning] No progress in {self.stall_threshold_s}s")
            return True
        return False

class Tee:
    """Duplicate output to multiple files."""
    def __init__(self, *files):
        self.files = files
        
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            
    def flush(self):
        for f in self.files:
            f.flush()

def main(g, time_limit_s=None, stall_threshold_s=600):
    start_time = time.time()
    y = 3 * g + 2
    print(f"[Init] Partitioning 3-subsets of {{0..{y-1}}} with g={g}")
    
    # Precompute combinatorial objects
    pairs = list(combinations(range(y), 2))
    triples = list(combinations(range(y), 3))
    P = len(pairs)
    T = len(triples)
    print(f"[Info] y={y}, pairs={P}, triples={T}")

    # Create mappings
    pair_index = {p: i for i, p in enumerate(pairs)}
    triple_index = {t: i for i, t in enumerate(triples)}
    
    # Precompute relationships in single pass
    triples_for_pair = [[] for _ in range(P)]
    pairs_for_triple = [[] for _ in range(T)]
    element_coverage = {}
    
    for pi, (a, b) in enumerate(pairs):
        for ti, t in enumerate(triples):
            if a not in t and b not in t:
                triples_for_pair[pi].append(ti)
                pairs_for_triple[ti].append(pi)
                # Build element coverage mapping
                for e in t:
                    key = (pi, e)
                    if key not in element_coverage:
                        element_coverage[key] = []
                    element_coverage[key].append(ti)
    
    # Create model
    model = cp_model.CpModel()
    x = {}
    for pi in range(P):
        for ti in triples_for_pair[pi]:
            x[(pi, ti)] = model.NewBoolVar(f"x_{pi}_{ti}")
    print(f"[Model] Created {len(x)} variables")

    # Constraints
    for pi in range(P):
        model.Add(sum(x[(pi, ti)] for ti in triples_for_pair[pi]) == g)

    for (pi, e), tis in element_coverage.items():
        model.AddExactlyOne([x[(pi, ti)] for ti in tis])

    for ti in range(T):
        if pairs_for_triple[ti]:
            model.AddExactlyOne([x[(pi, ti)] for pi in pairs_for_triple[ti]])

    # Strong symmetry breaking: Fix entire group for pair (0,1)
    if (0, 1) in pair_index:
        pi0 = pair_index[(0, 1)]
        fixed_triples = [
            (2 + 3*i, 3 + 3*i, 4 + 3*i)
            for i in range(g)
            if 4 + 3*i < y
        ]
        for t in fixed_triples:
            if t in triple_index:
                ti = triple_index[t]
                if (pi0, ti) in x:
                    model.Add(x[(pi0, ti)] == 1)
    
    # Configure solver
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 12 # Multiprocessing using number of cores
    solver.parameters.search_branching = cp_model.AUTOMATIC_SEARCH
    solver.parameters.log_search_progress = False
    if time_limit_s:
        solver.parameters.max_time_in_seconds = time_limit_s

    # Solve with progress monitoring
    callback = ProgressCallback(stall_threshold_s)
    status = solver.SolveWithSolutionCallback(model, callback)
    status_name = solver.StatusName(status)
    
    # Output results
    elapsed = time.time() - start_time
    print(f"[Result] Status: {status_name}")
    print(f"[Info] Total runtime: {int(elapsed // 3600)}h {int((elapsed % 3600) // 60)}m {elapsed % 60:.2f}s")
    
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return

    # Write solution
    filename = f"g{g}_solution.txt"
    with open(filename, 'w') as f:
        tee = Tee(f)
        for pi, (a, b) in enumerate(pairs):
            group = [
                triples[ti] 
                for ti in triples_for_pair[pi] 
                if solver.Value(x[(pi, ti)])
            ]
            triples_str = ",".join(map(str, group))
            tee.write(f"Group {pi+1}\t(omitted pair: ({a}, {b})): \t[{triples_str}]\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimized triple partition solver")
    parser.add_argument("--g", type=int, required=True, help="Triples per group")
    parser.add_argument("--time_limit", type=int, help="Solver timeout in seconds")
    parser.add_argument("--stall_threshold", type=int, default=600, help="Stall detection threshold")
    args = parser.parse_args()
    main(args.g, args.time_limit, args.stall_threshold)