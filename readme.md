# Pentomino Project
## SaT Encoder and solver for placing pentominos in a custom grid

The goal for this project is to find assignments to place pentominos in non-overlapping positions such that they fill a tiling grid. Pentominoes are shapes made of 5 square tiles that connect adjacently to at least one other piece. Like tetris pieces but with 5 tiles per shape instead of 4.

### Basic example

Imagine pentominoes A and B:
```
A A       B
A       B B B
A A       B
```

Now imagine they need to be inserted into the following grid:
```
[ ][ ][ ]
[ ][ ][ ][ ]
[ ][ ][ ]
```

It's easy to see the only valid assignment is 
```
[A][A][B]
[A][B][B][B]
[A][A][B]
```

In general, we want to ensure a two things: 
1. Each pentomino has a valid assignment in the grid
2. Each grid space is only inhabited by exactly one pentomino tile

### Formalizing the example
First, some vocabulary:
- Grid: The region to fill with pentominos
- Space: A single cell in the grid
- Space index: The index of a space in a grid
- Tile: A single assigned cell
- Pentomino: A collection of 5 adjacent tiles
- Assignment: A mapping of a tile to a space index
- Position: A collection of assignments that represents the position of a pentomino. In a valid position, every tile of the pentomino must have an assignment to some space index such that the pentomino's shape is maintained. Pentominos can be rotated (depending on the pentomino they have 1, 2, or 4 unique rotations) but cannot be reflected.
- Position set: The set of all possible positions a pentomino can have.

To formally place pentominos in a non-overlapping manner, we first want to find all it's possible positions. To do this, we'll first want to assign space indices to our grid. Continuing with the previous example, we have
```
[1][2][3]
[4][5][6][0]
[7][8][9]
```

To quantify our pentomino positions we use assignment variables. For example, ```A8``` is an assignment variable that is true if pentomino A occupies space 8 and false if it does not. A valid position is just a collection of assignment variables that follows the rules

All the valid positions for pentomino A:
```
A1, A2, A4, A7, A8
A2, A3, A5, A8, A9
A1, A2, A5, A7, A8
A2, A3, A6, A8, A9
A1, A2, A3, A4, A6
A4, A5, A6, A7, A9
A1, A3, A4, A5, A6
A4, A6, A7, A8, A9
```

All the valid positions for pentomino B:
```
B2, B4, B5, B6, B8
B3, B5, B6, B0, B9
```

Pentomino A will be in one of its 8 possible positions, which can be encoded as the following boolean expression:
```
  (A1 ^ A2 ^ A4 ^ A7 ^ A8)
v (A2 ^ A3 ^ A5 ^ A8 ^ A9)
v (A1 ^ A2 ^ A5 ^ A7 ^ A8)
v (A2 ^ A3 ^ A6 ^ A8 ^ A9)
v (A1 ^ A2 ^ A3 ^ A4 ^ A6)
v (A4 ^ A5 ^ A6 ^ A7 ^ A9)
v (A1 ^ A3 ^ A4 ^ A5 ^ A6)
v (A4 ^ A6 ^ A7 ^ A8 ^ A9)
```

And pentomino B will be in one of its 2 possible positions,
which can be encoded as the following boolean expression:
```
  (B2 ^ B4 ^ B5 ^ B6 ^ B8)
v (B3 ^ B5 ^ B6 ^ B0 ^ B9)
```
However, SaT solvers can only work with expressions in conjunctive normal form (CNF), which looks like 
```
(A1 v A2 v ... v An) ^ (B1 v B2 v ... v Bn) ^ ... ^ (Z1 v Z2 v ... v Zn)
```

Basically each expression is a disjunction of conjunctive clauses. Fortunately we can transform our expression into CNF in a fairly straightforward way using some extra variables. The possible positions for pentomino A can be written in CNF as
```
  (~Pa1 v A1) ^ (~Pa1 v A2) ^ (~Pa1 v A4) ^ (~Pa1 v A7) ^ (~Pa1 v A8) ^ (Pa1 v ~A1 v ~A2 v ~A4 v ~A7 v ~A8)
^ (~Pa2 v A2) ^ (~Pa2 v A3) ^ (~Pa2 v A5) ^ (~Pa2 v A8) ^ (~Pa2 v A9) ^ (Pa2 v ~A2 v ~A3 v ~A5 v ~A8 v ~A9)
^ (~Pa3 v A1) ^ (~Pa3 v A2) ^ (~Pa3 v A5) ^ (~Pa3 v A7) ^ (~Pa3 v A8) ^ (Pa3 v ~A1 v ~A2 v ~A5 v ~A7 v ~A8)
^ (~Pa4 v A2) ^ (~Pa4 v A3) ^ (~Pa4 v A6) ^ (~Pa4 v A8) ^ (~Pa4 v A9) ^ (Pa4 v ~A2 v ~A3 v ~A6 v ~A7 v ~A9)
^ (~Pa5 v A1) ^ (~Pa5 v A2) ^ (~Pa5 v A3) ^ (~Pa5 v A4) ^ (~Pa5 v A6) ^ (Pa5 v ~A1 v ~A2 v ~A3 v ~A4 v ~A6)
^ (~Pa6 v A4) ^ (~Pa6 v A5) ^ (~Pa6 v A6) ^ (~Pa6 v A7) ^ (~Pa6 v A9) ^ (Pa6 v ~A4 v ~A5 v ~A6 v ~A7 v ~A9)
^ (~Pa7 v A1) ^ (~Pa7 v A3) ^ (~Pa7 v A4) ^ (~Pa7 v A5) ^ (~Pa7 v A6) ^ (Pa7 v ~A1 v ~A3 v ~A4 v ~A5 v ~A6)
^ (~Pa8 v A4) ^ (~Pa8 v A6) ^ (~Pa8 v A7) ^ (~Pa8 v A8) ^ (~Pa8 v A9) ^ (Pa8 v ~A4 v ~A6 v ~A7 v ~A8 v ~A9)

^ (Sa v ~Pa1) ^ (Sa v ~Pa2) ^ (Sa v ~Pa3) ^ (Sa v ~Pa4) 
^ (Sa v ~Pa5) ^ (Sa v ~Pa6) ^ (Sa v ~Pa7) ^ (Sa v ~Pa8) 
^ (~Sa v Pa1 v Pa2 v Pa3 v Pa4 v Pa5 v Pa6 v Pa7 v Pa8)

^ Sa
```
Let's talk about the expression in more detail:
- A1...A9 are assignment variables. We've already seen these - A1 = True means that space 1 is occupied by pentomino A and A1 = False means that space 1 is not occupied by pentomino A
- Pa1...Pa8 are position variables. Pa1 = True means that pentomino A is in position 1 and Pa1 = False means that pentomino A is not in position 1
- Sa is a position set variable. Sa = True means that pentomino A has a position and Sa = False means that pentomino B doesn't have a position
- Clauses like (~Pa1 v A1) are called position-implies-assignment (PIA) components. Since all clauses must be true, this clause must be satisfied. It can be satisfied in two ways: either Pa1 is False, which means pentomino A is not in position 1, or we are in position 1, in which case we need A1 to be True. So in full, PIA components that given a position, all the all the requisite assignments are upheld, hence the name. 
- A collection of PIA components for a given position, such as (~Pa1 v A1) ^ (~Pa1 v A2) ^ (~Pa1 v A4) ^ (~Pa1 v A7) ^ (~Pa1 v A8), are called a PIA expression, because they represent the full PIA condition.
- Clauses like (Pa1 v ~A1 v ~A2 v ~A4 v ~A7 v ~A8) are called AIP clauses. Without these clauses it's possible that the position variable is true but not all the corresponding assignment variables are true. This takes care of the second direction of implication so that ```P <-> A1 ^ ... ^ An```.
- The pairing of a corresponding PIA expression and AIP clause is called an assignment-correspond-position (ACP) group, because it makes sure that assignments and positions correspond.
- The collection of all ACP groups (one for every possible position) is called an ACP block.
- Clauses like (Sa v ~Pa1) are called position-implies-set (PIS) components. They can be satisfied in two ways: either Pa1 is False which means pentomino A is not in position 1, or Pa1 is True, which means pentomino A is in position 1, in which case we need Sa to be true. So in full, these clauses ensure that if a given position variable is true, then the pentomino has a position. 
- A collection of PIS components for a given position set, such as ^ (Sa v ~Pa1) ^ (Sa v ~Pa2) ^ (Sa v ~Pa3) ^ (Sa v ~Pa4) ^ (Sa v ~Pa5) ^ (Sa v ~Pa6) ^ (Sa v ~Pa7) ^ (Sa v ~Pa8), are called a PIS expression, because they represent the full PIS condition.
- Clauses like (~Sa v Pa1 v Pa2 v Pa3 v Pa4 v Pa5 v Pa6 v Pa7 v Pa8) are called SIP clauses. They can be satisfied if Sa = False, which means pentomino A doesn't have a position, or pentomino A has a position, in which case we need at least one of the position variables to be True. So a SIP clause ensures that if a given position set variable is true, then the pentomino has a position.
- The clause Sa is called the position set requirement clause, because it ensures that the pentomino is in some position.
- The pairing of a corresponding PIS expression and SIP clause is called an SCP group, because it makes sure that a given position set corresponds with the piece being in at least one position. Note that this allows for each piece to be in multiple positions. However, the fact that the grid size should be the same as the number of pentominos times five (the number of tiles in each pentomino) ensures that any pentomino in multiple positions will overlap with another pentomino's position, a situation which is prohibited by a later set of clauses.
- The combination of the ACP block, SCP group, and set requirement clause for a given pentomino is called a placement section.

For completeness, here is the placement section for pentomino B:
```
  (~Pb1 v B2) ^ (~Pb1 v B4) ^ (~Pb1 v B5) ^ (~Pb1 v B6) ^ (~Pb1 v B8) 
^ (Pb1 v ~B2 v ~B4 v ~B5 v ~B6 v ~B8) # ^ Pb1
^ (~Pb2 v B3) ^ (~Pb2 v B5) ^ (~Pb2 v B6) ^ (~Pb2 v B0) ^ (~Pb2 v B9) 
^ (Pb2 v ~B3 v ~B5 v ~B6 v ~B0 v ~B9) # ^ Pb2

^ (Sb v ~Pb1) ^ (Sb v ~Pb2) ^ (~Sb v Pb1 v Pb2)

^ Sb
```

- The collection of all placement sections is called the permutation definition, since it's clauses say that all the pentominoes need to be in some permutation of positions.

As alluded to earlier, we also need to ensure that placements cannot overlap. This can be encoded as follows: 
```
  (~EaS1 v A1) ^ (~EaS1 v ~B1) ^ (EaS1 v ~A1 v B1)
^ (~EbS1 v ~A1) ^ (~EbS1 v B1) ^ (EbS1 v A1 v ~B1)
^ (EaS1 v EbS1)

<Repeat this for all other spaces>
```
Let's talk about this expression in more detail too:
- A1 and B1 are still assignment variables
- EaS1 is an exclusivity variable. EaS1 = True means that exclusively pentomino A is in space 1. EaS1 = False means that not exclusively pentomino A is in space 1
- (~EaS1 v A1) is an exclusivity-implies-assignments (EIA) component. It can be satisfied in two ways: either EaS1 = False, meaning it's not the case that pentomino A is exclusively in space 1, or EaS1 = True, meaning pentomino A IS exclusively in space 1, which means pentomino A must occupy space 1. So in full, EIA components ensure that a tile's exclusive position implies position (all assignments).
- A collection of EIA components for a given space, such as (~EaS1 v A1) ^ (~EaS1 v ~B1), are called an EIA expression, because they represent the full EIA condition
- Clauses like (EaS1 v ~A1 v B1) are AIE clauses. They can be satisfied in two ways: either at least one of the assignment literals is True (meaning a tile from pentomino A is either not assigned to space 1 or it's not the only tile assigned to space 1) or the assignment literals are all False (meaning pentomino A is the only assignment at space 1), which means that EaS1 must be True. So an AIE clause ensures that a single tile assigned to a space implies the exclusivity variable is True.
- The pairing of a corresponding EIA expression and AIE clause is called an assignment-correspond-exclusivity (ACE) group, because it makes sure that sole assignments and exclusivities correspond.
- There is an ACE group for every possible exclusivity (exclusively pentomino A, exclusively pentomino B, etc). Together, they make an exclusivity block.
- Clauses like (EaS1 v EbS1) are called occupancy clauses, because they ensure at least one pentomino will have a tile occupying that space. Note that multiple pentominos occupying a space is prohibited by ACE groups, because when multiple exclusivity variables are true, EIA components from different ACE groups simplify to conflict with each other. For example, if EaS1 and EbS1 are true, then (~EaS1 v A1) and (~EbS1 v ~A1) conflict.
- An exclusivity block and an occupancy clause combine to form a space sectiopn, because they define the full requirements for a given space.
- There is a space section for every space in the grid, and together they all form a grid definition, because they encode the occupancy of all spaces in the grid.

The permutation definition and grid definition completely specify the problem in terms of a SAT expression. This is what is logically generated by generate_cnf.py. However, we need to encode this expression into the DIMACS CNF format accepted by my OCaml SAT solver.

In the DIMACS CNF format, all variables must be numbers 1...n. Clauses look like
```
1 5 6 0
1 -2 3 0
-4 0
```
Where negative sign negates a literal, each variable on the same line is conjuncted to form clauses that are terminated by 0's and each line is a clause that is disjuncted with the other lines. If A maps to 1, B to 2, and so on, the above CNF translates to
```
(A v E v F) ^ (A v ~B v C) ^ (~D)
```
The SAT solver tries to find a satisfying assignment. If it does it will return an assignment for each number (x for True, -x for False).

To start, we have to count how many variables there are as a function of the input system. While we're at it, we might as well determine the number of clauses as a function of the input too. It will help to define ```total_positions``` as the number of positions of all pentominos. That is, ```num_positions(p0) + ... + num_positions(pn)``` for n pentominos. 

It will also help to define some sizes:
- ```G```: number of spaces in the grid
- ```N```: number of pentominos
- ```P_i```: number of positions for pentomino i
- ```T```: number of total positions (```T = P_0 + ... + P_N```)
- ```S```: size of a pentomino, 5 for our purposes

Assignment variables:
- ```G*N``` assignment variables, one for every pentomino at every space

Position variables:
- ```T``` position variables, one for every valid position for every pentomino

Position set variables:
- ```N``` position set variables, one for every pentomino

Exclusivity variables:
- ```G*N``` exclusivity variables, one for exclusive presence of every pentomino at every space

There is 1 SAT formula to be solved, which has a permutation definition and a grid definition.
There is 1 permuation definition, which has ```N``` placement sections.
There are ```N``` placement sections, which each have 1 ACP block, 1 SCP group, and 1 set requirement clause.
There are ```N``` ACP blocks which each have ```P_i``` ACP groups, making ```T``` ACP groups in total.
There are ```T``` ACP groups, which each have 1 PIA expression and 1 AIP clause.
There are ```T``` PIA expressions, which each have S PIA components.
There are ```TS``` PIA components, each containing 1 assignment variable and 1 placement variable.
There are ```T``` AIP clauses, which each have ```S``` assignment variables and 1 placement variable.
There are ```N``` SCP groups, which each have 1 PIS expression and 1 SIP clause
There are ```N``` PIS expressions, which each have ```P_i``` PIS components, making ```T``` PIS components in total.
There are ```T``` PIS components, which each have 1 position variable and 1 position set variable.
There are ```N``` SIP clauses, which each have ```P_i``` position variables and 1 position set variable.
There are ```N``` set requirement clauses, which each have 1 position set variable. 
There is 1 grid definition, which has ```G``` space sections.
There are ```G``` space sections, which each have 1 exclusivity block and 1 occupancy clause.
There are ```G``` exclusivity blocks, which each have ```N``` ACE groups.
There are ```GN``` ACE groups, which each have 1 EIA expression and 1 AIE clause.
There are ```GN``` EIA expressions, each containing ```N``` EIA components.
There are ```GN^2``` EIA components, which each have 1 assignment variable and 1 exclusivity variable.
There are ```GN``` AIE clauses, which each have ```N``` assignment variables and 1 exclusivity variable.
There are ```G``` occupancy clauses, which each have ```N``` exclusivity variables. 

So in total there are 
- ```TS``` PIA components (1a 1p) - ```2TS``` literals
- ```T``` AIP clauses (Sa 1p) - ```T(S+1)``` literals
- ```T``` PIS components (1p 1s) - ```2T``` literals
- ```N``` SIP clauses (Pip 1s) - ```T+N``` literals
- ```N``` set requirement clauses (1s) - ```N``` literals
- ```GN^2``` EIA components (1a 1e) - ```2GN^2``` literals
- ```GN``` AIE clauses (Na 1e) - ```GN(N+1)``` literals
- ```G``` occupancy clauses (Ne) - ```GN``` literals
- ```T(S+2) + 2N + G(N^2 + N + 1)``` clauses
- ```3TS + 4T + 3GN^2 + 2N(G+1)``` literals
- ```N(2G+1) + T``` unique variables

Now we can finally talk about giving numerical IDs to each variable.

Assignment variables will be assigned IDs ```1...GN```. As a reminder, assignment variables look like A4, which corresponds to pentomino A, space 4. An arbitrary assignment variable ps (pentomino, space) should be given id ```Gp + s + 1```.

Exclusivity variables will be assigned IDs ```GN+1...2GN```. As a reminder, exclusivity variables look like EbS3, which corresponds to pentomino B, space 3. An arbitrary exclusivity variable EpSs (Exclusively pentomino, Space space) should be given id ```GN + Gp + s + 1```.

Position variables will be assigned IDs ```2GN+1...2GN+T```. As a reminder, position variables look like Pb2, which corresponds to pentomino b, position 2. An arbitrary position variable Pbi (Position pentomino pos_id) should be given id ```2GN + O[p] + i + 1```. ```O``` is an array which holds offsets for each pentomino's position. Let's say there are three pentominos (A, B, and C). Pentomino A has 5 valid positions, pentomino B has 3, and pentomino C has 2, for a total of 10. Pa0 should have no offset, and Pa1...Pa4 should get the next 4 ids. Pb0 should have an offset of P_A = 5 so that it picks up the next id. Similarly, Pc0 should have an offset of P_A + P_B = 8 so that it picks up the next id after Pb0...Pb2.

Position set variables will be assigned IDs ```2GN+T+1...2GN+T+N```. As a reminder, position set variables look like Sc, which corresponds to pentomino C. An arbitrary position set variable Si (position set pentomino i) should have id ```2GN+T+i+1``` if i is 0-indexed.





```
  (~EaS1 v A1) ^ (~EaS1 v ~B1) ^ (~EaS1 v ~C1) ^ (EaS1 v ~A1 v B1 v C1)
^ (~EbS1 v ~A1) ^ (~EbS1 v B1) ^ (~EbS1 v ~C1) ^ (EbS1 v A1 v ~B1 v C1)
^ (~EcS1 v ~A1) ^ (~EcS1 v ~B1) ^ (~EcS1 v C1) ^ (EcS1 v A1 v B1 v ~C1)
^ (EaS1 v EbS1 v EcS1)

<Repeat this for all other spaces>
```


# don't we want it such that only one position is true at a time? 



