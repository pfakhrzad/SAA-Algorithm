from docplex.mp.model import Model
import pandas as pd
import numpy as np 
from collections import OrderedDict
import time
import sys

# Create a docplex model object
model = Model(name='CMWMS_SAA')

N1=2      # Number of Scenarios N
N2= 10     # Number of validation scenario
R= 1     # Repeatition
UncertanityLevel=0.1  # Uncertainity Level

print("================================================")
print("Number of Scenarios = ", N1," Validation Scenarios= ",N2)
print("Uncertainity Level= ", UncertanityLevel*100, "%" )
optimal_value={r0+1:0 for r0 in range(R)} # Optimal Value for all repeat
optimal_validation={r0+1:0 for r0 in range(R)} # Optimal value validaiton
Time_taken={r0+1:0 for r0 in range(R)}    # Time for all repeat
b_optimal = {}
br_optimal= {}
bj_optimal= {}
bc_optimal= {}

#=================================
# Sets
#=================================
# Load the Excel file
file_name = 'Data_Cplex.xlsx'   
excel = pd.ExcelFile(file_name)

h = excel.parse('delta', header=None, skiprows=1).iloc[:, 0].tolist()
j = excel.parse('UFxj',header=None, skiprows=0).iloc[0,1:].values.tolist()
n = list(OrderedDict.fromkeys(excel.parse('hy',header=None).iloc[1:,2].tolist()))
l = ['l1','l2']
k = ['k1','k2','k3','k4']
c = ['c1','c2']
r = ['r1','r2']
q = excel.parse('cap',header=None,skiprows=0).iloc[0,1:].values.tolist()
t = ['t1', 't2','t3']
x = excel.parse('d1',header=None,skiprows=0).iloc[0,1:].values.tolist()
y = excel.parse('d1',header=None,skiprows=0).iloc[0,1:].values.tolist()
z = excel.parse('d1',header=None,skiprows=0).iloc[0,1:].values.tolist()
s=[s0+1 for s0 in range(N1)]
s2=[s0+1 for s0 in range(N2)]

#=================================
# Scalar
#=================================
price = 100     # Income rate of recycleable waste disposal
pe = 0.09       # Selling price of unit electricity
capcr = 0.15    # Capacity of Recyclable waste container
ti = 24         # Number of collecting waste in planning horizon
vtr = 0.3       # Cost of transportation recycleable waste
vl = 0.3        # Transportation cost of residue to landfillsi
UFSeg = 100000  # Segregation faciliated cost per each machine
fxc = 100000    # Fixed cost of openning container center
betar = 0.5     # Fraction of disposal in recycling centers
alpha = 0.9     # Utilization rate of container sterilization
gama = 0.3      # Percentage of reducing unit price for selling reused container
M = 10000000000 # Big Number

#=================================
# Parameters
#=================================

uc = {} # Unit selling price of new c-type container for k-type waste
df=excel.parse(sheet_name='uc', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        uc[(row_label, col_label)] = value

ucr = {c0: value for c0, value in zip(c, excel.parse('ucr',header=None,skiprows=1).iloc[0,0:].values.tolist())} # Unit selling price of new c-type container for recycleable waste'
p = {k0:value  for k0,value in zip(k,excel.parse('p',header=None,skiprows=1).iloc[0,0:].values.tolist())}       # Income rate of k-type waste disposal'
pr ={r0:value  for r0,value in zip(r,excel.parse('pr',header=None,skiprows=1).iloc[0,0:].values.tolist())}      # Selling price of unit recycled product'

d1 = {}
df=excel.parse(sheet_name='d1', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        d1[(row_label, col_label)] = value
d2 = d1
d3 = {}
df=excel.parse(sheet_name='d2', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        d3[(row_label, col_label)] = value
d4 = d3
d6 = {}
df=excel.parse(sheet_name='d3', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        d6[(row_label, col_label)] = value
d5 =d6
fx = {} # Fixed cost of openning k-type collection center at level q'
df=excel.parse(sheet_name='fx', header=[0,1], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        fx[(row_label, col_label[0],col_label[1])] = value
UFx = {}# Fixed cost of facilated k-type collection center at level q'
df=excel.parse(sheet_name='UFx', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        UFx[(row_label, col_label)] = value
fxr = {}# Fixed cost of openning recycling center at level q'
df=excel.parse(sheet_name='fxr', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        fxr[(row_label, col_label)] = value
UFxr = {}# Fixed cost of facilated r-type recycling center at level q'
df=excel.parse(sheet_name='UFxr', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        UFxr[(row_label, col_label)] = value
fxj = {}# Fixed cost of openning j-tech treatment center at level q'
df=excel.parse(sheet_name='fxj', header=[0,1], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        fxj[(row_label, col_label[0],col_label[1])] = value

df=excel.parse(sheet_name='UFxj', header=[0], index_col=[0])
UFxj = {}# Fixed cost of facilated j-type treatment center at level q'
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        UFxj[(row_label, col_label)] = value
fxt = {t0: value for t0, value in zip(t, excel.parse('fxt',header=None,skiprows=1).iloc[0,0:].values.tolist())}  # Fixed cost of ordering t-type truck for one trip'

capc = {k0: value for k0, value in zip(k, excel.parse('capc',header=None,skiprows=1).iloc[0,0:].values.tolist())}  # Capacity of k-type waste container'
cap = {}# Capacity of k-type collection center at level q'  
df=excel.parse(sheet_name='cap', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        cap[(row_label, col_label)] = value
capr = {q0: value for q0, value in zip(q, excel.parse('capr',header=None,skiprows=1).iloc[0,0:].values.tolist())}# Capacity of recycling center at level q'
capj={} #  Capacity of j-tech treatment center at level q'
df=excel.parse(sheet_name='capj', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        capj[(row_label, col_label)] = value
capt = {t0: value for t0, value in zip(t, excel.parse('capt',header=None,skiprows=1).iloc[0,0:].values.tolist())} # 'capacity of t-type truck'
capl= {l0: value for l0, value in zip(l, excel.parse('capl',header=None,skiprows=1).iloc[0,0:].values.tolist())}  #  'capacity of landfill l'
MaxCap1={x1: value for x1, value in zip(x, excel.parse('Max',header=None,skiprows=1).iloc[0,0:].values.tolist())} #  'Maximum Available Capacity'
MaxCap2=MaxCap1 # Maximum Available Capacity in  nodes for recycling facilities
MaxCap3=MaxCap1 # Maximum Available Capacity for openning treatments'

comt={} # If k-type waste is compatible with t-type truck
df=excel.parse(sheet_name='comt', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        comt[(row_label, col_label)] = value
comj={} # If k-type waste is compatible with j-tech treatment
df=excel.parse(sheet_name='comj', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        comj[(row_label, col_label)] = value
comc={j0: value for j0, value in zip(j, excel.parse('comc',header=None,skiprows=1).iloc[0,0:].values.tolist())} # 'if reusable container is compatible with j-tech treatment'
comck={} # If k-type waste is compatible with c-type container
df=excel.parse(sheet_name='comck', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        comck[(row_label, col_label)] = value

v={} # Variable cost of transportation k-type waste per Ton/meter
df=excel.parse(sheet_name='v', header=[0], index_col=[0])
for row_label, row in df.iterrows():
    for col_label, value in row.iteritems():
        v[(row_label,col_label)] = value
vt={j0: value for j0, value in zip(j, excel.parse('vt',header=None,skiprows=1).iloc[0,0:].values.tolist())} #'variable cost of j-tech operation per unit waste'
vr={r0: value for r0, value in zip(r, excel.parse('vr',header=None,skiprows=1).iloc[0,0:].values.tolist())} # 'variable cost of recycling operation per unit r-type waste'
vs={k0: value for k0, value in zip(k, excel.parse('vs',header=None,skiprows=1).iloc[0,0:].values.tolist())}    #'variable cost of segregation operatio per unit k-type waste'

theta={h0: value for h0, value in zip(h, excel.parse('theta',header=None,skiprows=1).iloc[0,0:].values.tolist())}   # 'quality of recycleable waste segeration from 0-100% in generator h'
thetas={k0: value for k0, value in zip(k, excel.parse('thetas',header=None,skiprows=1).iloc[0,0:].values.tolist())} #  'fraction of recycleable waste in k-type waste'
betta={j0: value for j0, value in zip(j, excel.parse('betta',header=None,skiprows=1).iloc[0,0:].values.tolist())} #'fraction of disposal in j-tech treatment'
lambdaa={j0: value for j0, value in zip(j, excel.parse('lambda',header=None,skiprows=1).iloc[0,0:].values.tolist())} # 'electricity produced at j-tech treatment per ton'
lambdar={r0: value for r0, value in zip(r, excel.parse('lambdar',header=None,skiprows=1).iloc[0,0:].values.tolist())} #  'Amount of Recycled product r per tone'
lambdarbar={r0: value for r0, value in zip(r, excel.parse('lambdarbar',header=None,skiprows=1).iloc[0,0:].values.tolist())} # 'fraction of recyclable waste that can produce product r';
print("All Paramaeters loaded From Dataset,...")

#=================================
# UncertainParameters
#=================================
for iter in range(R):
    iter0=iter+1
    print("================================================")
    print("starting iteration: ",iter0)
    f = {s0: (1/N1) for s0 in s} #'occurance probability of scenario s'
    # Number of beds/patient filled yearly
    hy = {h0: value for h0, value in zip(h, excel.parse('hy',header=None,skiprows=1).iloc[0:,1].values.tolist())} 
    # category of each waste generator
    hn = {h0: n0 for h0, n0 in zip(h, excel.parse('hy',header=None,skiprows=1).iloc[0:,2].values.tolist())} 
    wperhn = {(n0,s0): 0 for n0 in n for s0 in s} # uncertain Waste production amount per each person 
    wg = {(h0,s0,k0):0 for h0 in h for k0 in k for s0 in s}
    wg2 = {(h0,s0):0 for h0 in h for s0 in s}

    print("Step 1:generatins scenarios...") 
    for s0 in s:
        Random_Cluster=np.random.rand() 
        if Random_Cluster<=0.1: # In Very low Cluster
            parameters = {"n1":0.5 ,"n2":0.5 ,"n3":0.05 ,"n4":0.05 ,"n5":0.25 ,"n6":0.40 ,"n7":0.15 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables.")
        elif Random_Cluster<=0.3 and Random_Cluster>0.1: # In  low Cluster
            parameters = {"n1":2.5 ,"n2":2.5 ,"n3":0.1 ,"n4":0.15 ,"n5":0.3 ,"n6":1.2 ,"n7":0.2 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables.")
        elif Random_Cluster<=0.7 and Random_Cluster>0.3: # In  medium Cluster
            parameters = {"n1":3.3 ,"n2":3.3 ,"n3":0.2 ,"n4":0.2  ,"n5":1.5 ,"n6":2.5 ,"n7":0.5 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables.")
        elif Random_Cluster<=0.9 and Random_Cluster>0.7: # In  high Cluster
            parameters = {"n1":6 ,"n2":6 ,"n3":1 ,"n4":1  ,"n5":2.5 ,"n6":3 ,"n7":1.25 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables.")
        elif Random_Cluster>0.9: # In  very high Cluster
            parameters = {"n1":11 ,"n2":9 ,"n3":1.5 ,"n4":2  ,"n5":5 ,"n6":3.5 ,"n7":2 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables.")
        else:
            print("There is an issue in generating random variables.")
            
        wginital = {(h0,s0): wperhn[hn[h0], s0] for h0 in h}
        kw= {"k1": .40, "k2": .13, "k3": 0.12, "k4": 0.15} # % of each type waste 
        for h0 in h:
            wg2[h0,s0]=max(round(wginital[h0,s0]*hy[h0]*0.2*0.001,3),0)
            for k0 in k:
                wg[h0,s0,k0]=max(round(wginital[h0,s0]*kw[k0]*hy[h0]*0.001,3),0)

    # Uncertain Waste production amount per each person     
    parameters = {"n1":0.2 ,"n2":0.5 ,"n3":0.7 ,"n4":0.3 ,"n5":0.3 ,"n6":0.4 ,"n7":0.3 }
    deltainitial = {(n0,s0): 0 for n0 in n for s0 in s} 
    for key in deltainitial.keys():
        if key[0] in parameters:
                mean = parameters[key[0]]
                deltainitial[key] = min(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),2),1)
        else:
                print("There is an issue in generating random variables in Delta.")

    delta = {(h0,s0): deltainitial[hn[h0], s0] for h0 in h for s0 in s}
    # for key in wperhn.keys():
        #     if key[0]=="n1":
        #         wperhn[key]=round(np.random.normal(loc=0.005, scale=UncertanityLevel*0.005),3)
        #     elif key[0]=="n2":
        #         wperhn[key]=round(np.random.normal(loc=0.005, scale=UncertanityLevel*0.005),3)
        #     elif key[0]=="n3":
        #         wperhn[key]=round(np.random.normal(loc=0.012, scale=UncertanityLevel*0.012),3)
        #     elif key[0]=="n4":
        #         wperhn[key]=round(np.random.normal(loc=0.015, scale=UncertanityLevel*0.015),3)
        #     elif key[0]=="n5":
        #         wperhn[key]=round(np.random.normal(loc=0.020, scale=UncertanityLevel*0.02),3)
        #     elif key[0]=="n6":
        #         wperhn[key]=round(np.random.normal(loc=0.020, scale=UncertanityLevel*0.02),3)
        #     elif key[0]=="n7":
        #         wperhn[key]=round(np.random.normal(loc=0.010, scale=UncertanityLevel*0.010),3)
        #     else:
        #         print("there is an issue in the generating random variables") 
    # wg2initial = {}
    # wperhnRecycle = {(n0,s0): 0 for n0 in n for s0 in s} # uncertain recycleable Waste production amount per each person 
    # for key in wperhnRecycle.keys():
    #     if key[0]=="n1":
    #         wperhnRecycle[key]=round(np.random.normal(loc=0.001, scale=UncertanityLevel*0.001),3)
    #     elif key[0]=="n2":
    #         wperhnRecycle[key]=round(np.random.normal(loc=0.005, scale=UncertanityLevel*0.005),3)
    #     elif key[0]=="n3":
    #         wperhnRecycle[key]=round(np.random.normal(loc=0.0012, scale=UncertanityLevel*0.0012),3)
    #     elif key[0]=="n4":
    #         wperhnRecycle[key]=round(np.random.normal(loc=0.0015, scale=UncertanityLevel*0.0015),3)
    #     elif key[0]=="n5":
    #         wperhnRecycle[key]=round(np.random.normal(loc=0.0020, scale=UncertanityLevel*0.002),3)
    #     elif key[0]=="n6":
    #         wperhnRecycle[key]=round(np.random.normal(loc=0.020, scale=UncertanityLevel*0.02),3)
    #     elif key[0]=="n7":
    #         wperhnRecycle[key]=round(np.random.normal(loc=0.010, scale=UncertanityLevel*0.01),3)
    #     else:
    #         print("there is an issue in the generating random variables") 
    # wg2inital = {(h0,s0): wperhnRecycle[hn[h0], s0] for h0 in h for s0 in s}   
    # delta={(h0,s0):round(np.random.normal(loc=0.3, scale=0.05),2) for h0 in h for s0 in s} #  'fraction of purchasing reusable container in scenario s by generator h'

    #================================================================
    # Variables
    #===============================================================
    print("Step 2: Modelling...")
    cost = model.continuous_var(name='cost')
    EC = model.continuous_var(name='EC')
    FC = model.continuous_var(name='FC')

    TR={s0: model.continuous_var(lb=0, name=f'TR_{s0}') for s0 in s}
    TC={s0: model.continuous_var(lb=0, name=f'TC_{s0}') for s0 in s}
    OC={s0: model.continuous_var(lb=0, name=f'OC_{s0}') for s0 in s}
    WR={s0: model.continuous_var(lb=0, name=f'WR_{s0}') for s0 in s}
    ERR={s0: model.continuous_var(lb=0, name=f'ERR_{s0}') for s0 in s}
    CR1={s0: model.continuous_var(lb=0, name=f'CR1_{s0}') for s0 in s}
    CR2={s0: model.continuous_var(lb=0, name=f'CR2_{s0}') for s0 in s}

    FilledCap1={(k0,x1,s0): model.continuous_var(name=f'testcap_{k0}_{x1}_{s0}') for k0 in k for x1 in x for s0 in s}
    FilledCap2={(y0,s0): model.continuous_var(name=f'testcap2_{y0}_{s0}') for y0 in y  for s0 in s}
    FilledCap3={(j0,z1,s0): model.continuous_var(name=f'testcap3_{j0}_{z1}_{s0}') for j0 in j for z1 in z for s0 in s}

    b = {(q0, k0, x1): model.binary_var(name=f'b_{q0}_{k0}_{x1}') for q0 in q for k0 in k for x1 in x}
    bc = {x1: model.binary_var(name=f'bc_{x1}') for x1 in x}
    br = {(q0, y1): model.binary_var(name=f'br_{q0}_{y1}') for q0 in q for y1 in y}
    bj = {(q0, j0, z1): model.binary_var(name=f'bj_{q0}_{j0}_{z1}') for q0 in q for j0 in j  for z1 in z}

    cn = {(h0, s0, c0, k0): model.integer_var(name=f'cn_{h0}_{s0}_{c0}_{k0}') for h0 in h  for s0 in s for c0 in c for k0 in k}
    cn2 = {(h0, s0, c0): model.integer_var(name=f'cn2_{h0}_{s0}_{c0}') for h0 in h  for s0 in s for c0 in c}

    w1 = {(h0,s0,k0,x1): model.continuous_var(lb=0, name=f'w1_{h0}_{s0}_{k0}_{x1}') for h0 in h  for s0 in s for k0 in k for x1 in x}
    cw1 = {(h0,s0,c0,k0,x1): model.integer_var(lb=0, name=f'cw1_{h0}_{s0}_{c0}_{k0}_{x1}') for h0 in h  for s0 in s for c0 in c for k0 in k for x1 in x }
    tr1 = {(h0,s0,t1,k0,x1): model.integer_var(lb=0, name=f'tr1_{h0}_{s0}_{t1}_{k0}_{x1}') for h0 in h  for s0 in s for t1 in t for k0 in k for x1 in x }

    w2 = {(h0,s0,y1): model.continuous_var(lb=0, name=f'w2_{h0}_{s0}_{y1}') for h0 in h  for s0 in s for y1 in y}
    cw2 = {(h0,s0,c0,y1): model.integer_var(lb=0, name=f'cw2_{h0}_{s0}_{c0}_{y1}') for h0 in h  for s0 in s for c0 in c for y1 in y }
    tr2 = {(h0,s0,t1,y1): model.integer_var(lb=0, name=f'tr2_{h0}_{s0}_{t1}_{y1}') for h0 in h  for s0 in s for t1 in t for y1 in y }

    w3 = {(k0,x1,s0,y1): model.continuous_var(lb=0, name=f'w3_{k0}_{x1}_{s0}_{y1}') for k0 in k for x1 in x for s0 in s for y1 in y}
    tr3 = {(k0,x1,s0,t1,y1): model.integer_var(lb=0, name=f'tr3_{k0}_{x1}_{s0}_{t1}_{y1}') for k0 in k for x1 in x for s0 in s for t1 in t for y1 in y }

    w4 = {(k0,x1,s0,j0,z1): model.continuous_var(lb=0, name=f'w4_{k0}_{x1}_{s0}_{j0}_{z1}') for k0 in k for x1 in x for s0 in s for j0 in j for z1 in z}
    cw4 = {(k0,x1,s0,j0,z1): model.integer_var(lb=0, name=f'cw4_{k0}_{x1}_{s0}_{j0}_{z1}') for k0 in k for x1 in x for s0 in s for j0 in j for z1 in z}
    tr4 = {(k0,x1,s0,t1,j0,z1): model.integer_var(lb=0, name=f'tr4_{k0}_{x1}_{s0}_{t1}_{j0}_{z1}') for k0 in k for x1 in x for s0 in s for t1 in t for j0 in j for z1 in z }

    cw5 = {(y1,s0,j0,z1): model.integer_var(lb=0, name=f'cw5_{y1}_{s0}_{j0}_{z1}') for y1 in y for s0 in s for j0 in j for z1 in z}

    wr1 ={(j0,z1,s0,l0): model.continuous_var(lb=0, name=f'wr1_{j0}_{z1}_{s0}_{l0}') for j0 in j for z1 in z for s0 in s for l0 in l}
    tr5= {(j0, z1, s0, t1, l0): model.integer_var(lb=0, name=f'tr5_{j0}_{z1}_{s0}_{t1}_{l0}') for j0 in j for z1 in z for s0 in s for t1 in t for l0 in l}

    wr2 ={(y1,s0,l0): model.continuous_var(lb=0, name=f'wr2_{y1}_{s0}_{l0}') for y1 in y for s0 in s for l0 in l}
    tr6 = {(y1, s0, t0, l0): model.integer_var(lb=0, name=f'tr6_{y1}_{s0}_{t0}_{l0}') for y1 in y for s0 in s for t0 in t for l0 in l}

    con1 = {(s0, k0, h0): model.integer_var(lb=0, name=f'con1_{s0}_{k0}_{h0}') for s0 in s for k0 in k for h0 in h }
    con2 = {(s0, h0): model.integer_var(lb=0, name=f'con2_{s0}_{h0}') for s0 in s for h0 in h }

    e = {(s0, j0, z1): model.continuous_var(lb=0, name=f'e_{s0}_{j0}_{z1}') for s0 in s for j0 in j for z1 in z}
    rp = {(s0,r1,y1): model.continuous_var(lb=0, name=f'rp_{s0}_{r1}_{y1}') for s0 in s for r1 in r for y1 in y}
    print("Decision variables defined successfully...")

    #=================================
    # Constraints
    #=================================
 
    # const8
    for h0 in h:
            for k0 in k: 
                for s0 in s:
                    model.add_constraint(model.sum(w1[h0,s0,k0,x1] for x1 in x) == model.sum(wg[h0,s0,k0]), ctname=f'const8_{h0}_{k0}_{s0}')

    # const9
    for h0 in h:
            for s0 in s:
                model.add_constraint(model.sum(w2[h0,s0,y1] for y1 in y) == model.sum(wg2[h0,s0]), ctname=f'const9_{h0}_{s0}')

    # const10
    for k0 in k:
        for x1 in x:
            for s0 in s:
                model.add_constraint(
                    model.sum(w1[h0, s0, k0, x1] for h0 in h ) ==
                    model.sum(w4[k0, x1, s0, j0, z1] for j0 in j for z1 in z) +
                    model.sum(w3[k0, x1, s0, y1] for y1 in y),
                    ctname=f'const10_{k0}_{x1}_{s0}'
                )
    # const11
    for k0 in k:
        for x1 in x:
            for s0 in s:
                model.add_constraint(
                    model.sum(w3[(k0, x1, s0, y1)] for y1 in y) ==
                    model.sum(w1[(h0, s0, k0, x1)] * (1 - theta[h0]) for h0 in h ) * thetas[k0],
                    ctname=f'const11_{k0}_{x1}_{s0}'
                )
    # const12
    for y1 in y:
        for s0 in s:
            model.add_constraint(
                model.sum(wr2[(y1, s0, l0)] for l0 in l) ==
                (model.sum(w2[(h0, s0, y1)] for h0 in h ) +
                model.sum(w3[(k0, x1, s0, y1)] for k0 in k for x1 in x)) * betar,
                ctname=f'const12_{y1}_{s0}'
            )
    # const13
    for j0 in j:
        for z1 in z:
            for s0 in s:
                model.add_constraint(
                    model.sum(wr1[(j0, z1, s0, l0)] for l0 in l) ==
                    model.sum(w4[(k0, x1, s0, j0, z1)] for k0 in k for x1 in x) * betta[j0],
                    ctname=f'const13_{j0}_{z1}_{s0}'
                )
    # const14
    for x1 in x:
        for k0 in k:
            for s0 in s:
                model.add_constraint(
                    model.sum(w1[(h0, s0, k0, x1)] * (1 / ti) for h0 in h ) <= 
                    model.sum(b[q0, k0, x1] * cap[k0, q0] for q0 in q),
                    ctname=f'const14_{x1}_{k0}_{s0}'
                )
                model.add_constraint(
                    FilledCap1[k0,x1,s0]==model.sum(w1[(h0, s0, k0, x1)] * (1 / ti) for h0 in h )
                )
    # const15
    for y1 in y:
        for s0 in s:
            model.add_constraint(
                model.sum(w2[(h0, s0, y1)] * (1 / ti) for h0 in h ) +
                model.sum(w3[(k0, x1, s0, y1)] * (1 / ti) for k0 in k for x1 in x) <= 
                model.sum(br[q0, y1] * capr[q0] for q0 in q),
                ctname=f'const15_{y1}_{s0}'
            )
            model.add_constraint(
                FilledCap2[y1,s0]==model.sum(w2[(h0, s0, y1)] * (1 / ti) for h0 in h ) +
                model.sum(w3[(k0, x1, s0, y1)] * (1 / ti) for k0 in k for x1 in x)
            )
    # const16
    for j0 in j:
        for z1 in z:
            for s0 in s:
                model.add_constraint(
                    model.sum(w4[(k0, x1, s0, j0, z1)] * (1 / ti) for k0 in k for x1 in x) <= 
                    model.sum(bj[q0, j0, z1] * capj[q0, j0] for q0 in q),
                    ctname=f'const16_{j0}_{z1}_{s0}'
                )
                model.add_constraint(
                    FilledCap3[j0,z1,s0]==model.sum(w4[(k0, x1, s0, j0, z1)] * (1 / ti) for k0 in k for x1 in x)
                )
    # const17
    for l0 in l:
        for s0 in s:
            model.add_constraint(
                model.sum(wr2[y1, s0, l0] * (1 / ti) for y1 in y) +
                model.sum(wr1[j0, z1, s0, l0] * (1 / ti) for j0 in j for z1 in z) <= 
                capl[l0],
                ctname=f'const17_{l0}_{s0}'
            )
    #Conmax1
    for x1 in x:
        model.add_constraint(
            model.sum(b[q0,k0,x1]*cap[k0,q0] for q0 in q for k0 in k) <= MaxCap1[x1],
            ctname=f'ConMax1_{x1}'
        )
    # const18
    for k0 in k:
        for j0 in j:
            for s0 in s:
                model.add_constraint(
                    model.sum(w4[(k0, x1, s0, j0, z1)] for x1 in x for z1 in z) <= comj[(k0, j0)]*M,
                    ctname=f'const18_{k0}_{j0}_{s0}'
            )
    # const19
    for j0 in j:
        for s0 in s:
            model.add_constraint(
                model.sum(cw5[(y1, s0, j0, z1)] for y1 in y for z1 in z) +
                model.sum(cw4[(k0, x1, s0, j0, z1)] for k0 in k for x1 in x for z1 in z) <= comc[j0]*M,
                ctname=f'const19_{j0}_{s0}'
            )
    # const20,200
    for x1 in x:
        model.add_constraint(model.sum(b[q0, k0, x1] for q0 in q for k0 in k) <= bc[x1] * M, ctname=f'const20_{x1}')
        model.add_constraint(model.sum(b[q0, 'k1', x1] + b[(q0, 'k3', x1)] + b[(q0, 'k4', x1)] for q0 in q) <= (1 - model.sum(b[q0, 'k2', x1] for q0 in q)) * M, ctname=f'const200_{x1}')
    # const21  
    for x1 in x:
        for z1 in z:
            if x1 == z1:
                model.add_constraint(model.sum(bj[q0, j0, z1] for q0 in q for j0 in j) <= (1-bc[x1]) * M, ctname=f'const21_{x1}_{z1}')
    # const211
    for z1 in z:
        model.add_constraint(model.sum(bj[q0, j0, z1] for q0 in q for j0 in j) <= 1, ctname=f'const211_{z1}')
    # const22         
    for y1 in y:
        for z1 in z:
            if y1 == z1:
                model.add_constraint(model.sum(br[q0, y1] for q0 in q) + model.sum(bj[q0, j0, z1] for q0 in q for j0 in j) <= 1, ctname=f'const22_{y1}_{z1}')
    # constdup1
    for x1 in x:
        model.add_constraint(model.sum(b[q0, 'k1', x1] for q0 in q )<=1, ctname=f'constdup1_{x1}')
        model.add_constraint(model.sum(b[q0, 'k2', x1] for q0 in q )<=1, ctname=f'constdup1_{x1}')
        model.add_constraint(model.sum(b[q0, 'k3', x1] for q0 in q )<=1, ctname=f'constdup3_{x1}')
        model.add_constraint(model.sum(b[q0, 'k4', x1] for q0 in q )<=1, ctname=f'constdup4_{x1}')
    # const23,233
    for h0 in h:
            for s0 in s:
                for t0 in t:
                    for k0 in k:
                        for x1 in x:
                            model.add_constraint(
                                tr1[h0,s0,t0,k0,x1] >= (w1[h0,s0,k0,x1]/capt[t0])*comt[k0,t0],
                                ctname=f'const23_{h0}_{s0}_{t0}_{k0}_{x1}'
                            )
                            model.add_constraint(
                                tr1[h0,s0,t0,k0,x1] - ((w1[h0,s0,k0,x1]/capt[t0])*comt[k0,t0]) <= 0.99999,
                                ctname=f'const233_{h0}_{s0}_{t0}_{k0}_{x1}'
                            )
    # const24,244
    for h0 in h:
            for s0 in s:
                for y1 in y:
                    model.add_constraint(
                        tr2[h0,s0,'t1',y1] >= w2[h0,s0,y1]/capt['t1'],
                        ctname=f'const24_{h0}_{s0}_{y1}'
                    )
                    model.add_constraint(
                        tr2[h0,s0,'t1',y1] - (w2[h0,s0,y1]/capt['t1']) <= 0.99999,
                        ctname=f'const244_{h0}_{s0}_{y1}'
                    )
    # const25,255,2555
    for k0 in k:
        for x1 in x:
            for s0 in s:
                for y1 in y:
                    model.add_constraint(
                        tr3[k0,x1,s0,'t1',y1] >= w3[k0,x1,s0,y1]/capt['t1'],
                        ctname=f'const25_{k0}_{x1}_{s0}_{y1}'
                    )
                    model.add_constraint(
                        tr3[k0,x1,s0,'t1',y1] - (w3[k0,x1,s0,y1]/capt['t1']) <= 0.99999,
                        ctname=f'const255_{k0}_{x1}_{s0}_{y1}'
                    )
                    model.add_constraint(
                        tr3[k0,x1,s0,'t1',y1] <= M*d3[x1,y1],
                        ctname=f'const2555_{k0}_{x1}_{s0}_{y1}'
                    )
    # const26,266
    for k0 in k:
        for x1 in x:
            for s0 in s:
                for t0 in t:
                    for j0 in j:
                        for z1 in z:
                            model.add_constraint(
                                tr4[k0,x1,s0,t0,j0,z1] >= (w4[k0,x1,s0,j0,z1]/capt[t0])*comt[k0,t0],
                                ctname=f'const26_{k0}_{x1}_{s0}_{t0}_{j0}_{z1}'
                            )
                            model.add_constraint(
                                tr4[k0,x1,s0,t0,j0,z1] - ((w4[k0,x1,s0,j0,z1]/capt[t0])*comt[k0,t0]) <= 0.99999,
                                ctname=f'const266_{k0}_{x1}_{s0}_{t0}_{j0}_{z1}'
                            )
    # const27,277
    for y1 in y:
        for s0 in s:
            for l0 in l:
                model.add_constraint(
                    tr6[y1,s0,'t3',l0] >= wr2[y1,s0,l0]/capt['t3'],
                    ctname=f'const27_{y1}_{s0}_{l0}'
                )
                model.add_constraint(
                    tr6[y1,s0,'t3',l0] - (wr2[y1,s0,l0]/capt['t3']) <= 0.99999,
                    ctname=f'const277_{y1}_{s0}_{l0}'
                )
    # const28,288
    for j0 in j:
        for z1 in z:
            for s0 in s:
                for l0 in l:
                    model.add_constraint(
                        tr5[j0,z1,s0,'t3',l0] >= wr1[j0,z1,s0,l0]/capt['t3'],
                        ctname=f'const28_{j0}_{z1}_{s0}_{l0}'
                    )
                    model.add_constraint(
                        tr5[j0,z1,s0,'t3',l0] - (wr1[j0,z1,s0,l0]/capt['t3']) <= 0.99999,
                        ctname=f'const288_{j0}_{z1}_{s0}_{l0}'
                    )
    # const29,299
    for h0 in h:
            for s0 in s:
                for k0 in k:
                    model.add_constraint(
                        cn[h0,s0,'c1',k0] >= (((model.sum(w1[h0,s0,k0,x1] for x1 in x))/(capc[k0]))/ti)*delta[h0,s0]*comck['c1',k0],
                        ctname=f'const29_{h0}_{s0}_{k0}'
                    )
                    model.add_constraint(
                        cn[h0,s0,'c1',k0] - ((((model.sum(w1[h0,s0,k0,x1] for x1 in x))/(capc[k0]))/ti)*delta[h0,s0]*comck['c1',k0]) <= 0.99999,
                        ctname=f'const299_{h0}_{s0}_{k0}'
                    )

    # const30,300
    for h0 in h:
            for s0 in s:
                for k0 in k:
                    model.add_constraint(
                        cn[h0,s0,'c2',k0] >= ((((model.sum(w1[h0,s0,k0,x1] for x1 in x))/(capc[k0]))/ti)-cn[h0,s0,'c1',k0]),
                        ctname=f'const30_{h0}_{s0}_{k0}'
                    )
                    model.add_constraint(
                        cn[h0,s0,'c2',k0] - ((((model.sum(w1[h0,s0,k0,x1] for x1 in x))/(capc[k0]))/ti)-cn[h0,s0,'c1',k0]) <= 0.99999,
                        ctname=f'const300_{h0}_{s0}_{k0}'
                    )
    # const31,311
    for h0 in h:
            for s0 in s:
                model.add_constraint(
                    cn2[h0,s0,'c1'] >= (model.sum(w2[h0,s0,y1] for y1 in y)/(capcr*ti))*delta[h0,s0],
                    ctname=f'const31_{h0}_{s0}'
                )
                model.add_constraint(
                    cn2[h0,s0,'c1'] - (model.sum(w2[h0,s0,y1] for y1 in y)/(capcr*ti))*delta[h0,s0] <= 0.99999,
                    ctname=f'const311_{h0}_{s0}'
                )
    # const32,322
    for h0 in h:
            for s0 in s:
                model.add_constraint(
                    cn2[h0,s0,'c2'] >= (((model.sum(w2[h0,s0,y1] for y1 in y))/(capcr*ti))-cn2[h0,s0,'c1']),
                    ctname=f'const32_{h0}_{s0}'
                )
                model.add_constraint(
                    cn2[h0,s0,'c2'] - ((model.sum(w2[h0,s0,y1] for y1 in y)/(capcr*ti))-cn2[h0,s0,'c1']) <= 0.99999,
                    ctname=f'const322_{h0}_{s0}'
                )
    # const33, 333
    for h0 in h:
            for s0 in s:
                for k0 in k:
                    for x1 in x:
                        model.add_constraint(
                            model.sum(cw1[h0,s0,c0,k0,x1] for c0 in c) >= w1[h0,s0,k0,x1]/(capc[k0]*ti),
                            ctname=f'const33_{h0}_{s0}_{k0}_{x1}'
                        )
                        model.add_constraint(
                            model.sum(cw1[h0,s0,c0,k0,x1] for c0 in c) - w1[h0,s0,k0,x1]/(capc[k0]*ti) <= 0.99999,
                            ctname=f'const333_{h0}_{s0}_{k0}_{x1}'
                        )
    # const34,344
    for h0 in h:
            for s0 in s:
                for k0 in k:
                    model.add_constraint(
                        model.sum(cw1[h0,s0,'c1',k0,x1] for x1 in x) <= cn[h0,s0,'c1',k0],
                        ctname=f'const34_{h0}_{s0}_{k0}'
                    )
                    model.add_constraint(
                        model.sum(cw1[h0,s0,'c2',k0,x1] for x1 in x) <= cn[h0,s0,'c2',k0],
                        ctname=f'const344_{h0}_{s0}_{k0}'
                    )
    # const35,355
    for h0 in h:
            for s0 in s:
                for y1 in y:
                    model.add_constraint(
                        model.sum(cw2[h0,s0,c0,y1] for c0 in c) >= w2[h0,s0,y1]/(capcr*ti),
                        ctname=f'const35_{h0}_{s0}_{y1}'
                    )
                    model.add_constraint(
                        model.sum(cw2[h0,s0,c0,y1] for c0 in c) - w2[h0,s0,y1]/(capcr*ti) <= 0.99999,
                        ctname=f'const355_{h0}_{s0}_{y1}'
                    )
    # const36,366
    for h0 in h:
            for s0 in s:
                model.add_constraint(
                    model.sum(cw2[h0,s0,'c1',y1] for y1 in y) <= cn2[h0,s0,'c1'],
                    ctname=f'const36_{h0}_{s0}'
                )
                model.add_constraint(
                    model.sum(cw2[h0,s0,'c2',y1] for y1 in y) <= cn2[h0,s0,'c2'],
                    ctname=f'const366_{h0}_{s0}'
                )
    # const37
    for k0 in k:
        for x1 in x:
            for s0 in s:
                model.add_constraint(
                    model.sum(cw4[k0,x1,s0,j0,z1] for j0 in j for z1 in z) == model.sum(cw1[h0,s0,'c1',k0,x1] for h0 in h ),
                    ctname=f'const37_{k0}_{x1}_{s0}'
                )
    # const38
    for y1 in y:
        for s0 in s:
            model.add_constraint(
                model.sum(cw5[y1,s0,j0,z1] for j0 in j for z1 in z) == model.sum(cw2[h0,s0,'c1',y1] for h0 in h ),
                ctname=f'const38_{y1}_{s0}'
            )
    # const39
    for j0 in j:
        for z1 in z:
            for s0 in s:
                model.add_constraint(
                    model.sum(cw4[k0,x1,s0,j0,z1] for k0 in k for x1 in x) + model.sum(cw5[y1,s0,j0,z1] for y1 in y) <= model.sum(capj[q0,j0]*bj[q0,j0,z1] for q0 in q),
                    ctname=f'const39_{j0}_{z1}_{s0}'
                )
    # const40
    for s0 in s:
        model.add_constraint(
            model.sum(con1[s0,k0,h0] for k0 in k for h0 in h ) == 
            model.sum(cw4[k0,x1,s0,j0,z1] for k0 in k for x1 in x for j0 in j for z1 in z),
            ctname=f'const40_{s0}'
        )
    # const400
    for k0 in k:
        for h0 in h:
                for s0 in s:
                    model.add_constraint(
                        con1[s0,k0,h0] <= cn[h0,s0,'c1',k0],
                        ctname=f'const400_{k0}_{h0}_{s0}'
                    )
    # const41
    for s0 in s:
        model.add_constraint(
            model.sum(con2[s0,h0] for h0 in h ) ==
            model.sum(cw5[y1,s0,j0,z1] for y1 in y for j0 in j for z1 in z),
            ctname=f'const41_{s0}'
        )
    # const411
    for h0 in h:
            for s0 in s:
                model.add_constraint(
                    con2[s0,h0] <= cn2[h0,s0,'c1'],
                    ctname=f'const411_{h0}_{s0}'
                )
    # const46
    for j0 in j:
        for z1 in z:
            for s0 in s:
                model.add_constraint(
                    e[s0,j0,z1] == (model.sum(w4[k0,x1,s0,j0,z1] for k0 in k for x1 in x)) * lambdaa[j0],
                    ctname=f'const46_{j0}_{z1}_{s0}'
                )
    # const47
    for r0 in r:
        for y1 in y:
            for s0 in s:
                model.add_constraint(
                    rp[s0,r0,y1] == ((model.sum(w2[h0,s0,y1] for h0 in h ))
                                    + (model.sum(w3[k0,x1,s0,y1] for k0 in k for x1 in x))) * lambdarbar[r0] * lambdar[r0],
                    ctname=f'const47_{r0}_{y1}_{s0}'
                )
    print("Constraints defined successfully...")

    #==================================================================
    # Objective function
    #==================================================================
    costEC=model.add_constraint(EC==model.sum(fx[q0,x0,k0]*b[q0,k0,x0] for q0 in q for x0 in x for k0 in k )+
                                    model.sum(fxc*bc[x0] for x0 in x)+
                                    model.sum(fxr[q0,y0]*br[q0,y0] for q0 in q for y0 in y)+
                                    model.sum(fxj[q0,z0,j0]*bj[q0,j0,z0] for q0 in q for z0 in z for j0 in j))

    costFC = model.add_constraint(FC==model.sum(UFx[q0,k0]*b[q0,k0,x0] for q0 in q for k0 in k for x0 in x) +
                                        model.sum(UFxr[q0,r0]*br[q0,y0] for q0 in q for y0 in y for r0 in r) +
                                        model.sum(UFxj[q0,j0]*bj[q0,j0,z0] for q0 in q for z0 in z for j0 in j))
    for s0 in s:
        model.add_constraint(TR[s0]== model.sum(fxt[t0]*(
                                    model.sum(tr1[h0,s0,t0,k0,x0] for h0 in h  for k0 in k for x0 in x)+
                                    model.sum(tr2[h0,s0,t0,y0] for h0 in h  for y0 in y)+
                                    model.sum(tr4[k0,x0,s0,t0,j0,z0] for k0 in k for x0 in x for j0 in j for z0 in z)+
                                    model.sum(tr3[k0,x0,s0,t0,y0] for k0 in k for x0 in x for y0 in y)+
                                    model.sum(tr6[y0,s0,t0,l0] for y0 in y for l0 in l)+
                                    model.sum(tr5[j0,z0,s0,t0,l0] for j0 in j for z0 in z for l0 in l)) for t0 in t)
                            )

        model.add_constraint(TC[s0] == model.sum(w1[h0,s0,k0,x0]*d1[h0,x0]*v[t0,k0] for h0 in h  for k0 in k for x0 in x for t0 in t)+
                                    model.sum(w2[h0,s0,y0]*d2[h0,y0]*vtr for h0 in h  for y0 in y)+
                                    model.sum(w3[k0,x0,s0,y0]*d3[x0,y0]*vtr for k0 in k for x0 in x for y0 in y)+
                                    model.sum(w4[k0,x0,s0,j0,z0]*d4[x0,z0]*v[t0,k0] for k0 in k for x0 in x for j0 in j for z0 in z for t0 in t)+
                                    model.sum(wr2[y0,s0,l0]*d5[y0,l0]*vl for y0 in y for l0 in l)+
                                    model.sum(wr1[j0,z0,s0,l0]*d6[z0,l0]*vl for j0 in j for z0 in z for l0 in l)
                            )
        model.add_constraint(OC[s0] == model.sum(vt[j0]*(model.sum(w4[k0,x0,s0,j0,z0] for k0 in k for x0 in x for z0 in z)+
                                                        model.sum(cw5[y0,s0,j0,z0]*ti for y0 in y for z0 in z)+
                                                        model.sum(cw4[k0,x0,s0,j0,z0]*ti for k0 in k for x0 in x for z0 in z))for j0 in j) +
                                    model.sum(vr[r0]*lambdarbar[r0]*(model.sum(w3[k0,x0,s0,y0] for k0 in k for x0 in x for y0 in y)+
                                                                model.sum(w2[h0,s0,y0] for h0 in h  for y0 in y))for r0 in r) +
                                    model.sum(vs[k0]*model.sum(w3[k0,x0,s0,y0] for x0 in x for y0 in y) for k0 in k)
                            )
        model.add_constraint(WR[s0] == model.sum(p[k0]*(model.sum(w1[h0,s0,k0,x0] for h0 in h  for x0 in x)) for k0 in k)+
                                    price*(model.sum(w2[h0,s0,y0] for h0 in h  for y0 in y))
                            )
        model.add_constraint(ERR[s0] == model.sum(pe*e[s0,j0,z0] for j0 in j for z0 in z)+
                            model.sum(pr[r0]*rp[s0,r0,y0] for r0 in r for y0 in y)
                            )
        model.add_constraint(CR1[s0] == model.sum(cn[h0,s0,'c1',k0]*uc['c1',k0] for h0 in h  for k0 in k) +
                                        model.sum(cn[h0,s0,'c2',k0]*ti*uc['c2',k0] for h0 in h  for k0 in k) +
                                        model.sum(cn2[h0,s0,'c1']*ucr['c1'] for h0 in h ) +
                                        model.sum(cn2[h0,s0,'c2']*ti*ucr['c2'] for h0 in h )
                            )
        model.add_constraint(CR2[s0] == gama * (model.sum(con1[s0,k0,h0]*ti*uc['c2',k0] for k0 in k for h0 in h ) +
                                            model.sum(con2[s0,h0]*ti*ucr['c2'] for h0 in h ))
                            )
    obj = model.minimize(EC+FC+model.sum((TR[s0]+TC[s0]+OC[s0]-WR[s0]-ERR[s0]-CR1[s0]-CR2[s0]) for s0 in s)/N1)
    print("Objective function is correct")
    #==============================================================
    # Solve
    #=============================================================
    print("Step 3: Solving the Model...")
    start_time = time.time()
    solution=model.solve(log_output=True)
    end_time = time.time()
    #assert solution
    print(f"The models was solved  for iteration {iter0} and the output will be exporting in the text file")
    print('Time taken:', end_time - start_time, 'seconds')
    print('Objective function value:', solution.get_objective_value())

    #=============================================================
    # Calculation 
    print('Time taken:', end_time - start_time, 'seconds')
    print('Objective function value:', solution.get_objective_value())
    for key in optimal_value.keys():
        if key==iter0:
            optimal_value[iter0]=solution.get_objective_value()
            Time_taken[iter0]=end_time - start_time
    # Loop through the keys of b and assign values to b_new
    for key in b.keys():
        b_optimal[iter0] = {key: max(solution.get_value(b[key]), 0) for key in b.keys()}
    for key in bc.keys():
        bc_optimal[iter0] = {key: max(solution.get_value(bc[key]),0) for key in bc.keys()}
    for key in bj.keys():
        bj_optimal[iter0] = {key: max(solution.get_value(bj[key]),0) for key in bj.keys()}
    for key in br.keys():
        br_optimal[iter0] = {key: max(solution.get_value(br[key]),0) for key in br.keys()}
    #==============================================================
    # Print results
    #=============================================================
    with open('MWMS_SAA_Output.txt', 'a') as f:
        # Redirect the console output to the file
        sys.stdout = f
        # Call the function that prints to the console
        if solution is not None:
                print("============================================")
                print("Result of Iteration:",iter0)
                model.print_information()
                solution.display()
                model.print_solution()
                print('Time taken:', end_time - start_time, 'seconds')
                print('Objective function value:', solution.get_objective_value())
                print(f"Objective value: {model.objective_value}")
                for key in b.keys():
                    if solution.get_value(b[key])>0.000:
                        print(f"b[{key}] value:", solution.get_value(b[key]))
                for key in bc.keys():
                    if solution.get_value(bc[key])>0.000:
                        print(f"bc[{key}] value:", solution.get_value(bc[key]))
                for key in br.keys():
                    if solution.get_value(br[key])>0.000:
                        print(f"br[{key}] value:", solution.get_value(br[key]))
                for key in bj.keys():
                    if solution.get_value(bj[key])>0.000:
                        print(f"bj[{key}] value:", solution.get_value(bj[key]))
                for key in wg.keys():
                    print(f"wg[{key}] waste generation:", wg[key])
                for key in wg2.keys():
                    print(f"wg2[{key}] recycleable waste generation:", wg2[key])
        else:
                print("Model is infeasible")
        # Reset the console output to its default
        sys.stdout = sys.__stdout__
    model.clear()
    del wg,wg2,delta

# Find the best solution  
f_optimalR = np.average(list(optimal_value.values()))
f_variancR= sum((optimal_value[r0+1] - f_optimalR) ** 2 for r0 in range(R)) / ((R-1)*R)
best_value_sample = max(optimal_value, key=optimal_value.get)
with open('MWMS_SAA_Output.txt', 'a') as f:
# Redirect the console output to the file
    sys.stdout = f
    print("==============================This is the Optimals at the end step1==========================")
    print(optimal_value)
    print(f"the iteration {best_value_sample} was the best Optimal value: ",min(optimal_value.values()))
    print(f"the Average of {R} iteration is : ",f_optimalR )
    print(f"The variance of {R} iteration is : ",f_variancR)
    print(b_optimal)
    print(bc_optimal)
    print(br_optimal)
    print(bj_optimal)
    sys.stdout = sys.__stdout__

print("==============================This is the Optimals at the end step1==========================")
print(optimal_value)
print(f"the iteration {best_value_sample} was the best Optimal value: ",max(optimal_value.values()))

#====================================================================================================
# Validation 
best_b=b_optimal[best_value_sample]
best_bc=bc_optimal[best_value_sample]
best_br=br_optimal[best_value_sample]
best_bj=bj_optimal[best_value_sample]
# solve the model again for N' scenario with the best solution of R samples
print("===========================================================================================")
print("starting validation stage")
for iter in range(R):
    iter0=iter+1
    print("================================================")
    print("starting iteration: ",iter0)
    s=s2
    f = {s0: (1/N2) for s0 in s} #'occurance probability of scenario s'
    hy = {h0: value for h0, value in zip(h, excel.parse('hy',header=None,skiprows=1).iloc[0:,1].values.tolist())} 
    hn = {h0: n0 for h0, n0 in zip(h, excel.parse('hy',header=None,skiprows=1).iloc[0:,2].values.tolist())} 
    wperhn = {(n0,s0): 0 for n0 in n for s0 in s} # uncertain Waste production amount per each person 
    wg = {(h0,s0,k0):0 for h0 in h for k0 in k for s0 in s}
    wg2 = {(h0,s0):0 for h0 in h for s0 in s}

    print("Step 1:generatins scenarios...") 
    for s0 in s:
        Random_Cluster=np.random.rand() 
        if Random_Cluster<=0.1: # In Very low Cluster
            parameters = {"n1":0.5 ,"n2":0.5 ,"n3":0.05 ,"n4":0.05 ,"n5":0.25 ,"n6":0.40 ,"n7":0.15 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables")
        elif Random_Cluster<=0.3 and Random_Cluster>0.1: # In  low Cluster
            parameters = {"n1":2.5 ,"n2":2.5 ,"n3":0.1 ,"n4":0.15 ,"n5":0.3 ,"n6":1.2 ,"n7":0.2 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables")
        elif Random_Cluster<=0.7 and Random_Cluster>0.3: # In  medium Cluster
            parameters = {"n1":3.3 ,"n2":3.3 ,"n3":0.2 ,"n4":0.2  ,"n5":1.5 ,"n6":2.5 ,"n7":0.5 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables")
        elif Random_Cluster<=0.9 and Random_Cluster>0.7: # In  high Cluster
            parameters = {"n1":6 ,"n2":6 ,"n3":1 ,"n4":1  ,"n5":2.5 ,"n6":3 ,"n7":1.25 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables")
        elif Random_Cluster>0.9: # In  very high Cluster
            parameters = {"n1":11 ,"n2":9 ,"n3":1.5 ,"n4":2  ,"n5":5 ,"n6":3.5 ,"n7":2 }
            for key in wperhn.keys():
                if key[0] in parameters:
                    mean = parameters[key[0]]
                    wperhn[key[0],s0] = max(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),3),0)
                else:
                    print("There is an issue in generating random variables")
        else:
            print("There is an issue in generating random variables.")
            
        wginital = {(h0,s0): wperhn[hn[h0], s0] for h0 in h}
        kw= {"k1": .40, "k2": .13, "k3": 0.12, "k4": 0.15} # % of each type waste 
        for h0 in h:
            wg2[h0,s0]=round(wginital[h0,s0]*hy[h0]*0.2*0.001,3)
            for k0 in k:
                wg[h0,s0,k0]=round(wginital[h0,s0]*kw[k0]*hy[h0]*0.001,3)

    # Uncertain Waste production amount per each person     
    parameters = {"n1":0.2 ,"n2":0.5 ,"n3":0.7 ,"n4":0.3  ,"n5":0.3 ,"n6":0.4 ,"n7":0.3 }
    deltainitial = {(n0,s0): 0 for n0 in n for s0 in s} 
    for key in deltainitial.keys():
        if key[0] in parameters:
                mean = parameters[key[0]]
                deltainitial[key] = min(round(np.random.normal(loc=mean, scale=UncertanityLevel*mean),2),1)
        else:
                print("There is an issue in generating random variables")
    delta = {(h0,s0): deltainitial[hn[h0], s0] for h0 in h for s0 in s}

    #================================================================
    # Variables
    #===============================================================
    cost = model.continuous_var(name='cost')
    EC = model.continuous_var(name='EC')
    FC = model.continuous_var(name='FC')

    TR={s0: model.continuous_var(lb=0, name=f'TR{s0}') for s0 in s}
    TC={s0: model.continuous_var(lb=0, name=f'TC{s0}') for s0 in s}
    OC={s0: model.continuous_var(lb=0, name=f'OC{s0}') for s0 in s}
    WR={s0: model.continuous_var(lb=0, name=f'WR{s0}') for s0 in s}
    ERR={s0: model.continuous_var(lb=0, name=f'ERR{s0}') for s0 in s}
    CR1={s0: model.continuous_var(lb=0, name=f'CR1{s0}') for s0 in s}
    CR2={s0: model.continuous_var(lb=0, name=f'CR2{s0}') for s0 in s}

    FilledCap1={(k0,x1,s0): model.continuous_var(name=f'testcap_{k0}_{x1}_{s0}') for k0 in k for x1 in x for s0 in s}
    FilledCap2={(y0,s0): model.continuous_var(name=f'testcap2_{y0}_{s0}') for y0 in y  for s0 in s}
    FilledCap3={(j0,z1,s0): model.continuous_var(name=f'testcap3_{j0}_{z1}_{s0}') for j0 in j for z1 in z for s0 in s}

    b = best_b
    bc = best_bc
    br = best_br
    bj = best_bj

    b = {(q0, k0, x1): model.binary_var(name=f'b_{q0}_{k0}_{x1}') for q0 in q for k0 in k for x1 in x}
    bc = {x1: model.binary_var(name=f'bc_{x1}') for x1 in x}
    br = {(q0, y1): model.binary_var(name=f'br_{q0}_{y1}') for q0 in q for y1 in y}
    bj = {(q0, j0, z1): model.binary_var(name=f'bj_{q0}_{j0}_{z1}') for q0 in q for j0 in j  for z1 in z}

    cn = {(h0, s0, c0, k0): model.integer_var(name=f'cn_{h0}_{s0}_{c0}_{k0}') for h0 in h  for s0 in s for c0 in c for k0 in k}
    cn2 = {(h0, s0, c0): model.integer_var(name=f'cn2_{h0}_{s0}_{c0}') for h0 in h  for s0 in s for c0 in c}

    w1 = {(h0,s0,k0,x1): model.continuous_var(lb=0, name=f'w1_{h0}_{s0}_{k0}_{x1}') for h0 in h  for s0 in s for k0 in k for x1 in x}
    cw1 = {(h0,s0,c0,k0,x1): model.integer_var(lb=0, name=f'cw1_{h0}_{s0}_{c0}_{k0}_{x1}') for h0 in h  for s0 in s for c0 in c for k0 in k for x1 in x }
    tr1 = {(h0,s0,t1,k0,x1): model.integer_var(lb=0, name=f'tr1_{h0}_{s0}_{t1}_{k0}_{x1}') for h0 in h  for s0 in s for t1 in t for k0 in k for x1 in x }

    w2 = {(h0,s0,y1): model.continuous_var(lb=0, name=f'w2_{h0}_{s0}_{y1}') for h0 in h  for s0 in s for y1 in y}
    cw2 = {(h0,s0,c0,y1): model.integer_var(lb=0, name=f'cw2_{h0}_{s0}_{c0}_{y1}') for h0 in h  for s0 in s for c0 in c for y1 in y }
    tr2 = {(h0,s0,t1,y1): model.integer_var(lb=0, name=f'tr2_{h0}_{s0}_{t1}_{y1}') for h0 in h  for s0 in s for t1 in t for y1 in y }

    w3 = {(k0,x1,s0,y1): model.continuous_var(lb=0, name=f'w3_{k0}_{x1}_{s0}_{y1}') for k0 in k for x1 in x for s0 in s for y1 in y}
    tr3 = {(k0,x1,s0,t1,y1): model.integer_var(lb=0, name=f'tr3_{k0}_{x1}_{s0}_{t1}_{y1}') for k0 in k for x1 in x for s0 in s for t1 in t for y1 in y }

    w4 = {(k0,x1,s0,j0,z1): model.continuous_var(lb=0, name=f'w4_{k0}_{x1}_{s0}_{j0}_{z1}') for k0 in k for x1 in x for s0 in s for j0 in j for z1 in z}
    cw4 = {(k0,x1,s0,j0,z1): model.integer_var(lb=0, name=f'cw4_{k0}_{x1}_{s0}_{j0}_{z1}') for k0 in k for x1 in x for s0 in s for j0 in j for z1 in z}
    tr4 = {(k0,x1,s0,t1,j0,z1): model.integer_var(lb=0, name=f'tr4_{k0}_{x1}_{s0}_{t1}_{j0}_{z1}') for k0 in k for x1 in x for s0 in s for t1 in t for j0 in j for z1 in z }

    cw5 = {(y1,s0,j0,z1): model.integer_var(lb=0, name=f'cw5_{y1}_{s0}_{j0}_{z1}') for y1 in y for s0 in s for j0 in j for z1 in z}

    wr1 ={(j0,z1,s0,l0): model.continuous_var(lb=0, name=f'wr1_{j0}_{z1}_{s0}_{l0}') for j0 in j for z1 in z for s0 in s for l0 in l}
    tr5= {(j0, z1, s0, t1, l0): model.integer_var(lb=0, name=f'tr5_{j0}_{z1}_{s0}_{t1}_{l0}') for j0 in j for z1 in z for s0 in s for t1 in t for l0 in l}

    wr2 ={(y1,s0,l0): model.continuous_var(lb=0, name=f'wr2_{y1}_{s0}_{l0}') for y1 in y for s0 in s for l0 in l}
    tr6 = {(y1, s0, t0, l0): model.integer_var(lb=0, name=f'tr6_{y1}_{s0}_{t0}_{l0}') for y1 in y for s0 in s for t0 in t for l0 in l}

    con1 = {(s0, k0, h0): model.integer_var(lb=0, name=f'con1_{s0}_{k0}_{h0}') for s0 in s for k0 in k for h0 in h }
    con2 = {(s0, h0): model.integer_var(lb=0, name=f'con2_{s0}_{h0}') for s0 in s for h0 in h }

    e = {(s0, j0, z1): model.continuous_var(lb=0, name=f'e_{s0}_{j0}_{z1}') for s0 in s for j0 in j for z1 in z}
    rp = {(s0,r1,y1): model.continuous_var(lb=0, name=f'rp_{s0}_{r1}_{y1}') for s0 in s for r1 in r for y1 in y}

    print("Decision variables defined successfully...")
    #=================================
    # Constraints
    #=================================
    # New COnstraints
    # for q0 in q:
    #     for k0 in k:
    #         for x1 in x:
    #             model.add_constraint(b[q0, k0, x1]==b_optimal[q0, k0, x1], ctname=f'constSAA_{q0}_{k0}_{x1}')
    # for x1 in x:
    #     model.add_constraint(bc[x1]==bc_optimal[x1],ctname=f'constSAA2_{x1}')
    # for q0 in q:
    #     for j0 in j:
    #         for z1 in z:
    #             model.add_constraint(bj[q0, j0, z1]==bj_optimal[q0, j0, z1],ctname=f'constSAA3_{q0}_{j0}_{z1}')
    # for q0 in q:
    #     for y1 in y:
    #         model.add_constraint(br[q0, y1]==br_optimal[q0, y1],ctname=f'constSAA4_{q0}_{y1}')

    # const8
    for h0 in h:
            for k0 in k: 
                for s0 in s:
                    model.add_constraint(model.sum(w1[h0,s0,k0,x1] for x1 in x) == model.sum(wg[h0,s0,k0]), ctname=f'const8_{h0}')

    # const9
    for h0 in h:
            for s0 in s:
                model.add_constraint(model.sum(w2[h0,s0,y1] for y1 in y) == model.sum(wg2[h0,s0]), ctname=f'const9_{h0}')

    # const10
    for k0 in k:
        for x1 in x:
            for s0 in s:
                model.add_constraint(
                    model.sum(w1[h0, s0, k0, x1] for h0 in h ) ==
                    model.sum(w4[k0, x1, s0, j0, z1] for j0 in j for z1 in z) +
                    model.sum(w3[k0, x1, s0, y1] for y1 in y),
                    ctname=f'const10_{k0}_{x1}_{s0}'
                )
    # const11
    for k0 in k:
        for x1 in x:
            for s0 in s:
                model.add_constraint(
                    model.sum(w3[(k0, x1, s0, y1)] for y1 in y) ==
                    model.sum(w1[(h0, s0, k0, x1)] * (1 - theta[h0]) for h0 in h ) * thetas[k0],
                    ctname=f'const11_{k0}_{x1}_{s0}'
                )
    # const12
    for y1 in y:
        for s0 in s:
            model.add_constraint(
                model.sum(wr2[(y1, s0, l0)] for l0 in l) ==
                (model.sum(w2[(h0, s0, y1)] for h0 in h ) +
                model.sum(w3[(k0, x1, s0, y1)] for k0 in k for x1 in x)) * betar,
                ctname=f'const12_{y1}_{s0}'
            )
    # const13
    for j0 in j:
        for z1 in z:
            for s0 in s:
                model.add_constraint(
                    model.sum(wr1[(j0, z1, s0, l0)] for l0 in l) ==
                    model.sum(w4[(k0, x1, s0, j0, z1)] for k0 in k for x1 in x) * betta[j0],
                    ctname=f'const13_{j0}_{z1}_{s0}'
                )
    # const14
    for x1 in x:
        for k0 in k:
            for s0 in s:
                model.add_constraint(
                    model.sum(w1[(h0, s0, k0, x1)] * (1 / ti) for h0 in h ) <= 
                    model.sum(b[q0, k0, x1] * cap[k0, q0] for q0 in q),
                    ctname=f'const14_{x1}_{k0}_{s0}'
                )
    # const15
    for y1 in y:
        for s0 in s:
            model.add_constraint(
                model.sum(w2[(h0, s0, y1)] * (1 / ti) for h0 in h ) +
                model.sum(w3[(k0, x1, s0, y1)] * (1 / ti) for k0 in k for x1 in x) <= 
                model.sum(br[q0, y1] * capr[q0] for q0 in q),
                ctname=f'const15_{y1}_{s0}'
            )

    # const16
    for j0 in j:
        for z1 in z:
            for s0 in s:
                model.add_constraint(
                    model.sum(w4[(k0, x1, s0, j0, z1)] * (1 / ti) for k0 in k for x1 in x) <= 
                    model.sum(bj[q0, j0, z1] * capj[q0, j0] for q0 in q),
                    ctname=f'const16_{j0}_{z1}_{s0}'
                )
    # const17
    for l0 in l:
        for s0 in s:
            model.add_constraint(
                model.sum(wr2[y1, s0, l0] * (1 / ti) for y1 in y) +
                model.sum(wr1[j0, z1, s0, l0] * (1 / ti) for j0 in j for z1 in z) <= 
                capl[l0],
                ctname=f'const17_{l0}_{s0}'
            )
    #Conmax1
    for x1 in x:
        model.add_constraint(
            model.sum(b[q0,k0,x1]*cap[k0,q0] for q0 in q for k0 in k) <= MaxCap1[x1],
            ctname=f'ConMax1_{x1}'
        )
    # const18
    for k0 in k:
        for j0 in j:
            for s0 in s:
                model.add_constraint(
                    model.sum(w4[(k0, x1, s0, j0, z1)] for x1 in x for z1 in z) <= comj[(k0, j0)]*M,
                    ctname=f'const18_{k0}_{j0}_{s0}'
            )
    # const19
    for j0 in j:
        for s0 in s:
            model.add_constraint(
                model.sum(cw5[(y1, s0, j0, z1)] for y1 in y for z1 in z) +
                model.sum(cw4[(k0, x1, s0, j0, z1)] for k0 in k for x1 in x for z1 in z) <= comc[j0]*M,
                ctname=f'const19_{j0}_{s0}'
            )
    # const20,200
    for x1 in x:
        model.add_constraint(model.sum(b[q0, k0, x1] for q0 in q for k0 in k) <= bc[x1] * M, ctname=f'const20_{x1}')
        model.add_constraint(model.sum(b[q0, 'k1', x1] + b[(q0, 'k3', x1)] + b[(q0, 'k4', x1)] for q0 in q) <= (1 - model.sum(b[q0, 'k2', x1] for q0 in q)) * M, ctname=f'const200_{x1}')
    # const21  
    for x1 in x:
        for z1 in z:
            if x1 == z1:
                model.add_constraint(model.sum(bj[q0, j0, z1] for q0 in q for j0 in j) <= (1-bc[x1]) * M, ctname=f'const21_{x1}_{z1}')
    # const211
    for z1 in z:
        model.add_constraint(model.sum(bj[q0, j0, z1] for q0 in q for j0 in j) <= 1)
    # const22         
    for y1 in y:
        for z1 in z:
            if y1 == z1:
                model.add_constraint(model.sum(br[q0, y1] for q0 in q) + model.sum(bj[q0, j0, z1] for q0 in q for j0 in j) <= 1, ctname=f'const22_{y1}_{z1}')
    # constdup1
    for x1 in x:
        model.add_constraint(model.sum(b[q0, 'k1', x1] for q0 in q )<=1, ctname=f'constdup1_{x1}')
        model.add_constraint(model.sum(b[q0, 'k2', x1] for q0 in q )<=1, ctname=f'constdup1_{x1}')
        model.add_constraint(model.sum(b[q0, 'k3', x1] for q0 in q )<=1, ctname=f'constdup3_{x1}')
        model.add_constraint(model.sum(b[q0, 'k4', x1] for q0 in q )<=1, ctname=f'constdup4_{x1}')

    # const23,233
    for h0 in h:
            for s0 in s:
                for t0 in t:
                    for k0 in k:
                        for x1 in x:
                            model.add_constraint(
                                tr1[h0,s0,t0,k0,x1] >= (w1[h0,s0,k0,x1]/capt[t0])*comt[k0,t0],
                                ctname=f'const23_{h0}_{s0}_{t0}_{k0}_{x1}'
                            )
                            model.add_constraint(
                                tr1[h0,s0,t0,k0,x1] - ((w1[h0,s0,k0,x1]/capt[t0])*comt[k0,t0]) <= 0.99999,
                                ctname=f'const233_{h0}_{s0}_{t0}_{k0}_{x1}'
                            )
    # const24,244
    for h0 in h:
            for s0 in s:
                for y1 in y:
                    model.add_constraint(
                        tr2[h0,s0,'t1',y1] >= w2[h0,s0,y1]/capt['t1'],
                        ctname=f'const24_{h0}_{s0}_{y1}'
                    )
                    model.add_constraint(
                        tr2[h0,s0,'t1',y1] - (w2[h0,s0,y1]/capt['t1']) <= 0.99999,
                        ctname=f'const244_{h0}_{s0}_{y1}'
                    )
    # const25,255,2555
    for k0 in k:
        for x1 in x:
            for s0 in s:
                for y1 in y:
                    model.add_constraint(
                        tr3[k0,x1,s0,'t1',y1] >= w3[k0,x1,s0,y1]/capt['t1'],
                        ctname=f'const25_{k0}_{x1}_{s0}_{y1}'
                    )
                    model.add_constraint(
                        tr3[k0,x1,s0,'t1',y1] - (w3[k0,x1,s0,y1]/capt['t1']) <= 0.99999,
                        ctname=f'const255_{k0}_{x1}_{s0}_{y1}'
                    )
                    model.add_constraint(
                        tr3[k0,x1,s0,'t1',y1] <= M*d3[x1,y1],
                        ctname=f'const2555_{k0}_{x1}_{s0}_{y1}'
                    )
    # const26,266
    for k0 in k:
        for x1 in x:
            for s0 in s:
                for t0 in t:
                    for j0 in j:
                        for z1 in z:
                            model.add_constraint(
                                tr4[k0,x1,s0,t0,j0,z1] >= (w4[k0,x1,s0,j0,z1]/capt[t0])*comt[k0,t0],
                                ctname=f'const26_{k0}_{x1}_{s0}_{t0}_{j0}_{z1}'
                            )
                            model.add_constraint(
                                tr4[k0,x1,s0,t0,j0,z1] - ((w4[k0,x1,s0,j0,z1]/capt[t0])*comt[k0,t0]) <= 0.99999,
                                ctname=f'const266_{k0}_{x1}_{s0}_{t0}_{j0}_{z1}'
                            )
    # const27,277
    for y1 in y:
        for s0 in s:
            for l0 in l:
                model.add_constraint(
                    tr6[y1,s0,'t3',l0] >= wr2[y1,s0,l0]/capt['t3'],
                    ctname=f'const27_{y1}_{s0}_{l0}'
                )
                model.add_constraint(
                    tr6[y1,s0,'t3',l0] - (wr2[y1,s0,l0]/capt['t3']) <= 0.99999,
                    ctname=f'const277_{y1}_{s0}_{l0}'
                )
    # const28,288
    for j0 in j:
        for z1 in z:
            for s0 in s:
                for l0 in l:
                    model.add_constraint(
                        tr5[j0,z1,s0,'t3',l0] >= wr1[j0,z1,s0,l0]/capt['t3'],
                        ctname=f'const28_{j0}_{z1}_{s0}_{l0}'
                    )
                    model.add_constraint(
                        tr5[j0,z1,s0,'t3',l0] - (wr1[j0,z1,s0,l0]/capt['t3']) <= 0.99999,
                        ctname=f'const288_{j0}_{z1}_{s0}_{l0}'
                    )
    # const29,299
    for h0 in h:
            for s0 in s:
                for k0 in k:
                    model.add_constraint(
                        cn[h0,s0,'c1',k0] >= (((model.sum(w1[h0,s0,k0,x1] for x1 in x))/(capc[k0]))/ti)*delta[h0,s0]*comck['c1',k0],
                        ctname=f'const29_{h0}_{s0}_{k0}'
                    )
                    model.add_constraint(
                        cn[h0,s0,'c1',k0] - ((((model.sum(w1[h0,s0,k0,x1] for x1 in x))/(capc[k0]))/ti)*delta[h0,s0]*comck['c1',k0]) <= 0.99999,
                        ctname=f'const299_{h0}_{s0}_{k0}'
                    )

    # const30,300
    for h0 in h:
            for s0 in s:
                for k0 in k:
                    model.add_constraint(
                        cn[h0,s0,'c2',k0] >= ((((model.sum(w1[h0,s0,k0,x1] for x1 in x))/(capc[k0]))/ti)-cn[h0,s0,'c1',k0]),
                        ctname=f'const30_{h0}_{s0}_{k0}'
                    )
                    model.add_constraint(
                        cn[h0,s0,'c2',k0] - ((((model.sum(w1[h0,s0,k0,x1] for x1 in x))/(capc[k0]))/ti)-cn[h0,s0,'c1',k0]) <= 0.99999,
                        ctname=f'const300_{h0}_{s0}_{k0}'
                    )
    # const31,311
    for h0 in h:
            for s0 in s:
                model.add_constraint(
                    cn2[h0,s0,'c1'] >= (model.sum(w2[h0,s0,y1] for y1 in y)/(capcr*ti))*delta[h0,s0],
                    ctname=f'const31_{h0}_{s0}'
                )
                model.add_constraint(
                    cn2[h0,s0,'c1'] - (model.sum(w2[h0,s0,y1] for y1 in y)/(capcr*ti))*delta[h0,s0] <= 0.99999,
                    ctname=f'const311_{h0}_{s0}'
                )
    # const32,322
    for h0 in h:
            for s0 in s:
                model.add_constraint(
                    cn2[h0,s0,'c2'] >= (((model.sum(w2[h0,s0,y1] for y1 in y))/(capcr*ti))-cn2[h0,s0,'c1']),
                    ctname=f'const32_{h0}_{s0}'
                )
                model.add_constraint(
                    cn2[h0,s0,'c2'] - ((model.sum(w2[h0,s0,y1] for y1 in y)/(capcr*ti))-cn2[h0,s0,'c1']) <= 0.99999,
                    ctname=f'const322_{h0}_{s0}'
                )
    # const33, 333
    for h0 in h:
            for s0 in s:
                for k0 in k:
                    for x1 in x:
                        model.add_constraint(
                            model.sum(cw1[h0,s0,c0,k0,x1] for c0 in c) >= w1[h0,s0,k0,x1]/(capc[k0]*ti),
                            ctname=f'const33_{h0}_{s0}_{k0}_{x1}'
                        )
                        model.add_constraint(
                            model.sum(cw1[h0,s0,c0,k0,x1] for c0 in c) - w1[h0,s0,k0,x1]/(capc[k0]*ti) <= 0.99999,
                            ctname=f'const333_{h0}_{s0}_{k0}_{x1}'
                        )
    # const34,344
    for h0 in h:
            for s0 in s:
                for k0 in k:
                    model.add_constraint(
                        model.sum(cw1[h0,s0,'c1',k0,x1] for x1 in x) <= cn[h0,s0,'c1',k0],
                        ctname=f'const34_{h0}_{s0}_{k0}'
                    )
                    model.add_constraint(
                        model.sum(cw1[h0,s0,'c2',k0,x1] for x1 in x) <= cn[h0,s0,'c2',k0],
                        ctname=f'const344_{h0}_{s0}_{k0}'
                    )
    # const35,355
    for h0 in h:
            for s0 in s:
                for y1 in y:
                    model.add_constraint(
                        model.sum(cw2[h0,s0,c0,y1] for c0 in c) >= w2[h0,s0,y1]/(capcr*ti),
                        ctname=f'const35_{h0}_{s0}_{y1}'
                    )
                    model.add_constraint(
                        model.sum(cw2[h0,s0,c0,y1] for c0 in c) - w2[h0,s0,y1]/(capcr*ti) <= 0.99999,
                        ctname=f'const355_{h0}_{s0}_{y1}'
                    )
    # const36,366
    for h0 in h:
            for s0 in s:
                model.add_constraint(
                    model.sum(cw2[h0,s0,'c1',y1] for y1 in y) <= cn2[h0,s0,'c1'],
                    ctname=f'const36_{h0}_{s0}'
                )
                model.add_constraint(
                    model.sum(cw2[h0,s0,'c2',y1] for y1 in y) <= cn2[h0,s0,'c2'],
                    ctname=f'const366_{h0}_{s0}'
                )
    # const37
    for k0 in k:
        for x1 in x:
            for s0 in s:
                model.add_constraint(
                    model.sum(cw4[k0,x1,s0,j0,z1] for j0 in j for z1 in z) == model.sum(cw1[h0,s0,'c1',k0,x1] for h0 in h ),
                    ctname=f'const37_{k0}_{x1}_{s0}'
                )
    # const38
    for y1 in y:
        for s0 in s:
            model.add_constraint(
                model.sum(cw5[y1,s0,j0,z1] for j0 in j for z1 in z) == model.sum(cw2[h0,s0,'c1',y1] for h0 in h ),
                ctname=f'const38_{y1}_{s0}'
            )
    # const39
    for j0 in j:
        for z1 in z:
            for s0 in s:
                model.add_constraint(
                    model.sum(cw4[k0,x1,s0,j0,z1] for k0 in k for x1 in x) + model.sum(cw5[y1,s0,j0,z1] for y1 in y) <= model.sum(capj[q0,j0]*bj[q0,j0,z1] for q0 in q),
                    ctname=f'const39_{j0}_{z1}_{s0}'
                )
    # const40
    for s0 in s:
        model.add_constraint(
            model.sum(con1[s0,k0,h0] for k0 in k for h0 in h ) == 
            model.sum(cw4[k0,x1,s0,j0,z1] for k0 in k for x1 in x for j0 in j for z1 in z),
            ctname=f'const40_{s0}'
        )
    # const400
    for k0 in k:
        for h0 in h:
                for s0 in s:
                    model.add_constraint(
                        con1[s0,k0,h0] <= cn[h0,s0,'c1',k0],
                        ctname=f'const400_{k0}_{h0}_{s0}'
                    )
    # const41
    for s0 in s:
        model.add_constraint(
            model.sum(con2[s0,h0] for h0 in h ) ==
            model.sum(cw5[y1,s0,j0,z1] for y1 in y for j0 in j for z1 in z),
            ctname=f'const41_{s0}'
        )
    # const411
    for h0 in h:
            for s0 in s:
                model.add_constraint(
                    con2[s0,h0] <= cn2[h0,s0,'c1'],
                    ctname=f'const411_{h0}_{s0}'
                )
    # const46
    for j0 in j:
        for z1 in z:
            for s0 in s:
                model.add_constraint(
                    e[s0,j0,z1] == (model.sum(w4[k0,x1,s0,j0,z1] for k0 in k for x1 in x)) * lambdaa[j0],
                    ctname=f'const46_{j0}_{z1}_{s0}'
                )
    # const47
    for r0 in r:
        for y1 in y:
            for s0 in s:
                model.add_constraint(
                    rp[s0,r0,y1] == ((model.sum(w2[h0,s0,y1] for h0 in h ))
                                    + (model.sum(w3[k0,x1,s0,y1] for k0 in k for x1 in x))) * lambdarbar[r0] * lambdar[r0],
                    ctname=f'const47_{r0}_{y1}_{s0}'
                )
    print("Constraints defined successfully...")
    #==================================================================
    # Objective function
    #==================================================================
    costEC=model.add_constraint(EC==model.sum(fx[q0,x0,k0]*b[q0,k0,x0] for q0 in q for x0 in x for k0 in k )+
                                    model.sum(fxc*bc[x0] for x0 in x)+
                                    model.sum(fxr[q0,y0]*br[q0,y0] for q0 in q for y0 in y)+
                                    model.sum(fxj[q0,z0,j0]*bj[q0,j0,z0] for q0 in q for z0 in z for j0 in j))

    costFC = model.add_constraint(FC==model.sum(UFx[q0,k0]*b[q0,k0,x0] for q0 in q for k0 in k for x0 in x) +
                                        model.sum(UFxr[q0,r0]*br[q0,y0] for q0 in q for y0 in y for r0 in r) +
                                        model.sum(UFxj[q0,j0]*bj[q0,j0,z0] for q0 in q for z0 in z for j0 in j))
    for s0 in s:
        model.add_constraint(TR[s0]== model.sum(fxt[t0]*(
                                    model.sum(tr1[h0,s0,t0,k0,x0] for h0 in h  for k0 in k for x0 in x)+
                                    model.sum(tr2[h0,s0,t0,y0] for h0 in h  for y0 in y)+
                                    model.sum(tr4[k0,x0,s0,t0,j0,z0] for k0 in k for x0 in x for j0 in j for z0 in z)+
                                    model.sum(tr3[k0,x0,s0,t0,y0] for k0 in k for x0 in x for y0 in y)+
                                    model.sum(tr6[y0,s0,t0,l0] for y0 in y for l0 in l)+
                                    model.sum(tr5[j0,z0,s0,t0,l0] for j0 in j for z0 in z for l0 in l)) for t0 in t)
                            )
        model.add_constraint(TC[s0] == model.sum(w1[h0,s0,k0,x0]*d1[h0,x0]*v[t0,k0] for h0 in h  for k0 in k for x0 in x for t0 in t)+
                                    model.sum(w2[h0,s0,y0]*d2[h0,y0]*vtr for h0 in h  for y0 in y)+
                                    model.sum(w3[k0,x0,s0,y0]*d3[x0,y0]*vtr for k0 in k for x0 in x for y0 in y)+
                                    model.sum(w4[k0,x0,s0,j0,z0]*d4[x0,z0]*v[t0,k0] for k0 in k for x0 in x for j0 in j for z0 in z for t0 in t)+
                                    model.sum(wr2[y0,s0,l0]*d5[y0,l0]*vl for y0 in y for l0 in l)+
                                    model.sum(wr1[j0,z0,s0,l0]*d6[z0,l0]*vl for j0 in j for z0 in z for l0 in l)
                            )
        model.add_constraint(OC[s0] == model.sum(vt[j0]*(model.sum(w4[k0,x0,s0,j0,z0] for k0 in k for x0 in x for z0 in z)+
                                                        model.sum(cw5[y0,s0,j0,z0]*ti for y0 in y for z0 in z)+
                                                        model.sum(cw4[k0,x0,s0,j0,z0]*ti for k0 in k for x0 in x for z0 in z))for j0 in j) +
                                    model.sum(vr[r0]*lambdarbar[r0]*(model.sum(w3[k0,x0,s0,y0] for k0 in k for x0 in x for y0 in y)+
                                                                model.sum(w2[h0,s0,y0] for h0 in h  for y0 in y))for r0 in r) +
                                    model.sum(vs[k0]*model.sum(w3[k0,x0,s0,y0] for x0 in x for y0 in y) for k0 in k)
                            )
        model.add_constraint(WR[s0] == model.sum(p[k0]*(model.sum(w1[h0,s0,k0,x0] for h0 in h  for x0 in x)) for k0 in k)+
                                    price*(model.sum(w2[h0,s0,y0] for h0 in h  for y0 in y))
                            )
        model.add_constraint(ERR[s0] == model.sum(pe*e[s0,j0,z0] for j0 in j for z0 in z)+
                            model.sum(pr[r0]*rp[s0,r0,y0] for r0 in r for y0 in y)
                            )
        model.add_constraint(CR1[s0] == model.sum(cn[h0,s0,'c1',k0]*uc['c1',k0] for h0 in h  for k0 in k) +
                                        model.sum(cn[h0,s0,'c2',k0]*ti*uc['c2',k0] for h0 in h  for k0 in k) +
                                        model.sum(cn2[h0,s0,'c1']*ucr['c1'] for h0 in h ) +
                                        model.sum(cn2[h0,s0,'c2']*ti*ucr['c2'] for h0 in h )
                            )
        model.add_constraint(CR2[s0] == gama * (model.sum(con1[s0,k0,h0]*ti*uc['c2',k0] for k0 in k for h0 in h ) +
                                            model.sum(con2[s0,h0]*ti*ucr['c2'] for h0 in h ))
                            )
    obj = model.minimize(EC+FC+model.sum((TR[s0]+TC[s0]+OC[s0]-WR[s0]-ERR[s0]-CR1[s0]-CR2[s0]) for s0 in s)/N2)
    print("Objective function is correct")

    #==============================================================
    # Solve
    #=============================================================
    start_time = time.time()
    solution=model.solve(log_output=True)
    end_time = time.time()
    assert solution
    print(f"The models was solved  for validation {iter0} and the outpu will be generating in the text file")
    #=============================================================
    # Calculation 
    print('Time taken:', end_time - start_time, 'seconds')
    print('Objective function value:', solution.get_objective_value())
    for key in optimal_validation.keys():
        if key==iter0:
            optimal_validation[iter0]=solution.get_objective_value()
    #==============================================================
    # Print results
    #=============================================================
    import sys
    with open('validation.txt', 'a') as f:
        # Redirect the console output to the file
        sys.stdout = f
        # Call the function that prints to the console
        if solution is not None:
                print("============================================")
                model.print_information()
                solution.display()
                model.print_solution()
                print('Time taken:', end_time - start_time, 'seconds')
                print('Objective function value:', solution.get_objective_value())
                print(f"Objective value: {model.objective_value}")
        else:
                print("Model is infeasible")
        print("the average of R iteration: ",f_optimalR)
        print("the variance of R iteration: ",f_variancR)
        print("The Gap is :",model.objective_value-f_optimalR)
        # Reset the console output to its default
        sys.stdout = sys.__stdout__
    print('Time taken:', end_time - start_time, 'seconds')
    print('Objective function value:', solution.get_objective_value())
    model.clear()
    del wg,wg2,delta

# Check the Versions
# import docplex 
# import cplex
# print("Docplex version:", docplex.__version__)
# print("CPLEX version:", cplex.__version__)