# CMWMS_SAA Repository

This repository contains code implementing the Stochastic Approximation Algorithm (SAA) for the Two-Stage Stochastic MILP CMWMS (Medical Waste Management System) problem.

## Description

The code in this repository utilizes the IBM CPLEX optimization library to solve the CMWMS problem using the Sample Average  Approximation Algorithm. The CMWMS problem involves optimizing a Network in a waste management system, considering uncertain factors.

## This is the SAA Algorithm used in this code

**Input:** Number of scenarios $N$, validation scenario $N'$, iteration $R$, $N' > > N$;

**Realization:**
1. $Gap = \infty$, $LB = \infty$, $UB = -\infty$,
2. For $r = 0, 1, 2, ..., R$, calculate $CF_N^r = \min\{C_1^Tb + \frac{1}{N}\sum_{n=1}^N y^n C_2(\xi^n)\}$,
3. Calculate the optimal objective value of R iterations: $\bar{CF_N^R} = \frac{1}{R}\sum_{r=1}^R CF_N^r$ and the variance $\sigma_{N,R}^2 = \frac{1}{(R-1)R}\sum_{r=1}^R(CF_N^r - \bar{CF_N^R})^2$, $LB = \bar{CF_N^R}$,
4. Pick one feasible solution from R iterations: $\bar{b_N^R} \in \{b_N^1, b_N^2, ..., b_N^R\}$,
5. Calculate the objective value of the original problem: $CF_{N'} = \min\{C_1^T\bar{b_N^R} + \frac{1}{N'}\sum_{n=1}^{N'} y^n C_2(\xi^n)\}$ and $UB = CF_{N'}$,
6. $Gap_{N,R,N'} = UB - LB$,
7. If $Gap_{N,R,N'} > Goal$, increase $N$ and $R$, and repeat from the realization step.
8. 
**Output:** When the Gap is less than the goal, the optimal solution is $\bar{b_N^R}$ for the first stage, and the optimal value is $CF_{N'}$.
       
## Code Overview

The main script, `main.py`, implements the SAA algorithm using the CPLEX library. The algorithm iteratively refines the solution by considering different scenarios and validating against a set of scenarios. The following steps are performed in the code:

1. Import necessary libraries including `docplex`, `pandas`, `numpy`, and others.
2. Create a CPLEX model object named 'CMWMS_SAA'.
3. Define problem parameters such as the number of scenarios, repetition count, uncertainty level, etc.
4. Define sets, scalars, and parameters needed for the optimization problem.
5. Iterate over scenarios and perform optimization using the SAA algorithm.
6. Capture and store optimal values, validation results, and execution times.


## Usage

1. Make sure you have Python and the required libraries installed.
2. Place your data in the `Data_Cplex.xlsx` file as per the expected format.
3. Run the `MWMS_SAA.py` script to execute the SAA algorithm and solve the Two-Stage Stochastic problem.

## Acknowledgments
The code in this repository is based on research in waste management optimization. If you find this code useful, please consider citing the relevant papers.

## License

---
Author: [Paria Fakhrzad]

