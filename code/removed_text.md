## Model 3: Exam timetabling with room merging

## Sets
$$
\begin{aligned}
C &: \text{ set of exams}, \\
T &: \text{ set of timeslots}, \\
R &: \text{ set of individuals rooms}, \\
G &: \text{ set of room group (super rooms)}, \\
S &: \text{ set of students}, \\
E_s &\subseteq C \text{ exams taken by student } s.
G_r &\subseteq R \text{ room belonging to group} r.
\end{aligned}
$$

## Parameters
$$
\begin{aligned}
dur_i &: \text{ duration of exam } i, \\
len_t &: \text{ length of timeslot } t, \\
cap_r &: \text{ capacity of room } r, \\
Cap_g = \sum_{r \in G_g} cap_r &: \text{super room capacity}, \\
size_i &: \text{ number of students taking exam } i.
\end{aligned}
$$

## Decision variables

### 1. Timeslot assignment
$$
x_{i,t} =
\begin{cases}
1 & \text{if exam } i \text{ is scheduled in timeslot } t, \\
0 & \text{otherwise}.
\end{cases}
$$

### 2. Use of individuals rooms
$$
z_{i,t,r} =
\begin{cases}
1 & \text{if exam } i \text{ uses room } r \text{ in timeslot } t, \\
0 & \text{otherwise}.
\end{cases}
$$

### 3. Use of super rooms (room merging)
$$
y_{i,t,g} =
\begin{cases}
1 & \text{if exam } i \text{ uses super room } g \text{ in timeslot } t, \\
0 & \text{otherwise}.
\end{cases}
$$

# Constraints

## 1. Each exam assigned exactly one timeslot
$$
\sum_{t \in T} x_{i,t} = 1 
\qquad \forall i \in C
$$

## 2. Linking: exam must be in timesplot before using rooms
Individual rooms: 
$$
z_{i,t,r} \le x_{i,t}
\qquad \forall i \in C,\; t \in T,\; r \in R
$$

Super rooms: 
$$
y_{i,t,g} \le x_{i,t}
\qquad \forall i \in C,\; t \in T,\; g \in G
$$

## 3. No student may have overlapping exams
$$
x_{i,t} + x_{j,t} \le 1
\qquad \forall s \in S,\; \forall i \neq j \in E_s,\; t \in T
$$

## 4. Capacity requirement with room merging
Exam $i$ receives capacity from: 
- individual room $r$
- or super room $g$

Total capacity must satisfy exam size:
$$
\sum_{r\in R} cap_r z_{i,t,r} + \sum_{g \in G} Cap_g y_{i,t,g} \geq size_i x_{i,t}
\qquad \forall i \in C, t \in T
$$

## 5. Super room occupancy activities all constituent rooms
If a super room group $g$ is used, then all of its rooms must be marked occupied:
$$
z_{i,t,r} \geq y_{i,t,g}
\qquad \forall g \in G, \forall r \in G_g,\; \forall i, t
$$

This ensures rooms in the group cannot be used by another exam.

## 6. No room can host more than one exam in a timeslot
$$
\sum_{i \in C} z_{i,t,r} \le 1
\qquad \forall t \in T,\; r \in R
$$

## 7. Exam duration feasibility  
$$
x_{i,t} = 0
\qquad \forall i \in C, t \in T \text { such that } dur_i > len_t
$$

# Objective
$$
\min 0
$$