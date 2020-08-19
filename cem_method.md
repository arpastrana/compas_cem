# Combinatorial Equilibrium Modelling

Ole Ohlbrock and Pierluigi D'Acunto, 2020 / Computer-Aided Design / ETH Zürich

## Overview
0. Initial State
1. Initialize $\mathbf{T}_0$ and $\mathbf{X}_0$
2. Check compatibility
3. Input $\mathbf{T}$ and $\mathbf{X}$
4. CEM Algorithm
5. Output $\mathbf{F}$ and $\mathbf{F}^*$
6. Evaluation
	7. Yes -> Further Design
	8. No -> Transformation -> Back to 3.
9. Final State

Constraints injected to 1., 3., and 6.

## Components

1. Form Diagram $\mathbf{F}$
2. Force Diagram $\mathbf{F}^*$
3. Topological Diagram $\mathbf{T}$

	_Graph of $\mathbf{F}$, depicts connectivity and combinatorial state of internal forces._
4. List of Design Parameters $\mathbf{X}$

## Topological Diagram $\mathbf{T}$

Two edge types:
- Trails (Avenues), $t_{ij}$
- Deviations (Streets), $d_{D_{ij}}$ , $d_{I_{ij}}$ 

One force state:
- Combinatorial state $c_{ij}$.

### Trail Edges
A _trail_ is a polyline with vertices $v_i$ made from individual _trail edges_ $t_{ij}$. It is the direct load path that transfers applied loads to a support.

- _origin vertices_: start points, correspond to origin nodes of form Diagram $\mathbf{F}$.
- _support vertices_: support points in $\mathbf{F}$.
- _topological distance_ $w$: number of trail segments between vertex $v_i$ and trail's support vertex. 
- _sequence_ $k$: Set of vertices with the same topological distance $w$. 

Two fundamental conditions:
1. Every vertex $v_i$ in $\mathbf{T}$ belongs exclusively to one trail.
2. Only a single support vertex exists at one extreme of a trail.

An equilibrium state will be found for any topological diagram $\mathbf{T}$ that fulfils the two rules above.

### Deviation Edges

Edge formed connecting two vertices from two different trails. Two types exist:

1. **Direct**: A direct deviation edge $d_{D_{ij}}$ connects two vertices $v_i$ in $\mathbf{T}$ that belong to the same sequence $k$.
2. **Indirect**: An indirect deviation edge $d_{I_{ij}}$ connects two vertices $v_i$ in $\mathbf{T}$ that belong to the different sequences $k$.

### Combinatorial states

A _combinatorial state_ $c_{ij}$ is used-defined for every trail and deviation edges of $\mathbf{T}$.


## Design Parameters $\mathbf{X}$

A list of design parameters of $\mathbf{F}$ that contains:
- position vectors, $\mathbf{p}$ of the origin nodes (one entry per trail).
- trail edges lengths, $\lambda_{ij}$
- deviation edges absolute force magnitudes, $\mu_{ij}*$
- external forces, $\mathbf{q}_{E, i}*$.

--- 

## Form-finding Algorithm

Inputs: 
-  Topological Diagram $\mathbf{T}$
- Design Parameters $\mathbf{X}$

Algebraical or geometrical process
1. Extract topological properties of the network (?)
2. Impose equilibrium **sequentially** based on $\mathbf{X}$.
3. Update iteratively equilibrium state if indirect deviation edges $d_{I_{ij}}$ or form-dependent load cases exists $\mathbf{q}_{E, i}^{(t)*}$.


### Step 1: Graph analysis

- Adjacency matrix $\mathbf{C}$

	Based on a topological Diagram $\mathbf{T}$, extract a symmetric adjacency matrix $\mathbf{C}$. Rows and columns correspond to vertices $v_i$, and entries correspond to combinatorial states of the edges: +1 for tension and -1 for compression.

- Sorted Adjacency matrix $\mathbf{C}'$

	Adjacency matrix $\mathbf{C}$ sorted by vertices $v_i$ topological distance $w_i$.
	
- Submatrix $\mathbf{D}_D$

	Direct deviation edges combinatorial states.

- Submatrix $\mathbf{D}_I$

	Indirect deviation edges combinatorial states.
	
- Submatrix $\mathbf{T}_{out}$

	Combinatorial states of the **outgoing*‌* trail edges
	
	
### Step 2: Explicit equilibrium imposition

If submatrix $\mathbf{D}_I$ is empty, e.g. no indirect deviation edges $d_{I_{ij}}$ exist, equilibrium can be calculated sequence-by-sequence, **without iterations**.

```
for sequence in sequences:
	for node in sequence:
		impose_equilibrium(node)
```


#### Outgoing trail **force** vector $\mathbf{t}_{i-out}^*$

For vertex $v_i$, an _outgoing trail **force** vector_, $\mathbf{t}_{i-out}^*$, is computed as:

$$\mathbf{t}_{i-out}^* = -\mathbf{t}_{i-in}^* -\mathbf{r} \mathbf{d}_{i-D}^* - \mathbf{q}_{E, i}^* \tag{1}$$

where:

- $\mathbf{t}_{i-in}^* = 0$ (if $k = 0$), or $= -\mathbf{t}_{i-out}^*$ (if $k > 0$).

- The resultant direct deviation vector, $\mathbf{r} \mathbf{d}_{i-D}^*$.


The resultant direct deviation vector, $\mathbf{r} \mathbf{d}_{i-D}^*$ is the sum of all direct deviation forces incoming to vertex $v_i$:

$$\mathbf{r} \mathbf{d}_{i-D}^* = \sum_{j=0}^m d_{ij}^* \mathbf{u}_{ij} = \sum_{j=0}^m c_{ij} \mu_{ij}^* \mathbf{u}_{ij}\tag{2}$$ 

where:

- Unit vector $\mathbf{u}_{ij}$ is:

$$\mathbf{u}_{ij} = \frac{\mathbf{p}_j - \mathbf{p}_i}{|| \mathbf{p}_j - \mathbf{p}_i ||} \tag{3}$$


#### Outgoing vertex **position** vector $\mathbf{p}_{i-out}$

The resulting position of vertex $v_i$ can be determined using the combinatorial state $c_{i-out}$ registered in $\mathbf{T}_out$, the absolute length $\lambda_{out}$ from design parameters $\mathbf{X}$, and the outgoing unit vector $\mathbf{u}_{i-out}$ obtained with $\mathbf{t}_{i-out}^*$:

$$\mathbf{p}_{i-out} = \mathbf{p}_{i-in} + t_{i-out} \mathbf{u}_{i-out}\tag{4}$$ 

$$\mathbf{p}_{i-out} = \mathbf{p}_{i-in} + c_{i-out} \lambda_{i-out} \frac{\mathbf{t}_{i-out}^*}{||\mathbf{t}_{i-out}^*||}\tag{5}$$

Consider that $\mathbf{p}_{i-in}$ in sequence $k$ is equal to $\mathbf{p}_{i-out}$ in previous sequence $k-1$, and that $\mathbf{p}_{i-in}$ equals to the initial position vectors at the origin nodes,  $\mathbf{p}$.

Reaction forces $\mathbf{s}_i^*$, missing edge lengths and force magnified can be obtained unequivocally.


Alternative paramterizations contemplate using a **Force Density** or a **Load Path** approach.


### Step 3: Iterative equilibrium

In the presence of indirect deviation edges, it is necessary to iterate a few times over the complete structure so that global equilibrium converges. This is because it is not possible to know in advance the direction of a deviation edge that connects two vertices which are part of two different sequences. The remedy to this is to go over equation (1) $n$ number of times until the total average position of the vertices of $\mathbf{T}$  are displaced less than a user-defined threshold. 

Equation (1) is extended to account for indirect deviation edges, $d_{I_{ij}}$, as follows: 

$$\mathbf{t}_{i-out}^{n} = -\mathbf{t}_{i-in}^{n} -\mathbf{r} \mathbf{d}_{i-D}^{n} - \mathbf{q}_{E, i}^{n} -\mathbf{r} \mathbf{d}_{i-I}^{n} \tag{6}$$

The resultant vector of indirect deviation edges $\mathbf{r} \mathbf{d}_{i-I}^{n}$ is homologous to equation 2 and set to **zero** in the first iteration step.

The convergence criteria to exit the iterative loop is set to:

$$\sum_i^{m} |\mathbf{p}_i^{t} - \mathbf{p}_i^{t-1}| < \epsilon \tag{7}$$

where $\epsilon = 1e-5$ from experimental tests.
