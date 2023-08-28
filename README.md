# CMWMS_SAA Repository

This repository contains code implementing the Stochastic Approximation Algorithm (SAA) based on CPLEX for the CMWMS (Medical Waste Management System) problem.

## Description

The code in this repository utilizes the IBM CPLEX optimization library to solve the CMWMS problem using the Sample Average  Approximation Algorithm. The CMWMS problem involves optimizing a Network in a waste management system, considering uncertain factors.

This is the SAA Algorithm used in this code :\\
\begin{frame}
\frametitle{SAA-Cplex}
\begin{figure}[H]
\tiny{
  \centering
  \fbox{\parbox{1\textwidth}{
    \textcolor{red}{\textit{Input:}} Number of scenarios $N$,validation scenario $N^'$, iteration $R$,  $N^{'} > > N$; \\
    \textcolor{red}{\textit{Realization}:} Generate $R$ independent sample of $N,N^'$ scenarios for$W_{k}^{hn(s)}, W^{hn(s)}$ and $\delta^{h(s)}$ ;\\
    \begin{enumerate}
        \item[1)] $Gap=\infty,LB=\infty, UB=-\infty$,  
        \item[2)]  for $r=0,1,2,..,R$, $CF_N^r=min\left\{C_1^Tb+\frac{1}{N}\sum_{n=1}^N y^n C_2(\xi^n) \right\}$
    \item[3)]  Calculate the optimal objective value of R iterations$\quad \bar{CF_N^R}=\frac{1}{R}\sum_{r=1}^R CF_N^r \quad $ and \\ the variance $ \quad \sigma_{N,R}^2=\frac{1}{(R-1)R}\sum_{r=1}^R\left(CF_N^r-\bar{CF_N^R}\right)^2$, 
          $LB=\bar{CF_N^R}$
    \item[4)] Pick one feasible solution from R iteration $\quad \bar{b_N^R} \in \{b_N^1,b_N^2,...b_N^R\}$
    \item[5)] Calculate the objective value of original problem $CF_{N'}=min\left\{C_1^T\bar{b_N^R}+\frac{1}{N'}\sum_{n=1}^{N'} y^n C_2(\xi^n) \right\}$ and $\quad UB=CF_{N'}$ 
    \item[6)] $\quad Gap_{N,R,N'}=UB-LB$, 
    \item[7)] if $Gap_{N,R,N'} > Goal$, increase $N$ and $R$ and repeat from realization step
    \end{enumerate}
    \textcolor{red}{\textit{Output:}} when the Gap is less than the goal so the optimal solution is $\bar{b_N^R}$ for first-stage and the optimal value is $CF_{N'}$ }}}
\end{figure}        
	\end{frame}
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

