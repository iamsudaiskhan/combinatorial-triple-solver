# combinatorial-triple-solver
Optimized Python algorithm that solves complex combinatorial assignment problems. Efficiently organizes triples into disjoint groups with unique omitted pairs, featuring massive performance improvements - solving g=8 cases in 55 minutes instead of 40+ hours.

# Combinatorial Triple Solver

A Python solution for organizing triples into groups with strict constraints, developed to solve a challenging combinatorial problem that required significant optimization.

## About This Project

This code addresses a specific combinatorial assignment problem where we need to:
- Arrange triples into groups of size `g`
- Ensure no triples are repeated
- Keep all triples within each group disjoint
- Assign unique omitted pairs to each group

The solution emerged from working through progressively more complex cases, with a focus on making previously intractable problems solvable in reasonable timeframes.

## Performance Progress

Here's how the solution evolved over time:

| Case | Initial Approach | Optimized Solution |
|------|-----------------|-------------------|
| g = 5 | ~3 hours | ~25 seconds |
| g = 8 | 40+ hours | ~55 minutes |
| g = 10 | Not feasible | Under 1 minute |

## How It Works

The implementation uses several optimization techniques:
- Google's OR-Tools for constraint satisfaction
- Careful constraint formulation to avoid redundancy
- Parallel processing to utilize available computing resources
- Efficient data structures for faster lookups
- Symmetry breaking to reduce the search space

## Getting Started

To use this code:

```bash
git clone https://github.com/yourusername/combinatorial-triple-solver.git
cd combinatorial-triple-solver
pip install -r requirements.txt


Solution Validation

Each solution is checked against these criteria:

Every triple appears exactly once
Groups contain only disjoint triples
Each group has a unique omitted pair
Output format works with standard validation tools
Technical Approach

The performance improvements came from:

Focusing on essential constraints only
Better handling of search space
Memory-efficient data management
Leveraging multiple CPU cores when available
License