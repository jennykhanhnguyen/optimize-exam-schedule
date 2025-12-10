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

Modelling the earliness

This is a classic variation of a **Weighted Completion Time** scheduling problem. You want to minimize the "cost" of delaying high-priority exams.

To achieve your specific requirements—treating all slots within a single day as roughly equal, but increasing the penalty significantly once the day changes—you should use a **Step Function** for your time slots.

Here is the mathematical model to calculate the penalty.

---

### 1. The Core Equation
We calculate the Total Penalty ($Z$) for a schedule as:

$$Z = \sum_{i \in \text{Exams}} \left( W(P_i) \times C(t_i) \right)$$

Where:
* $P_i$ is the priority of exam $i$ (0–99).
* $W(P_i)$ is the **Priority Weight** (how much we care about this exam).
* $t_i$ is the time slot assigned to exam $i$ (1–32).
* $C(t_i)$ is the **Time Slot Cost** (the penalty for using that specific slot).

Our goal is to **minimize** $Z$.

---

### 2. Modeling the Time Slot Cost, $C(t)$
This is the most critical part for your request. You want slots on the same day to be "relatively the same," with a jump in penalty when moving to the next day.

We define the cost of a slot based on its **Day Index** rather than its Slot Index.

#### Step A: Map Slots to Days
You have a repeating pattern of 16 slots per week (5 days $\times$ 3 slots + 1 Saturday $\times$ 1 slot).
Let $t$ be the slot number ($1 \dots 32$). We can calculate the Day Index $d(t)$ (ranging from 1 to 12) using this logic:

1.  **Calculate Week Number ($k$):**
    $$k = \lfloor \frac{t-1}{16} \rfloor$$
    *(Value is 0 for Week 1, 1 for Week 2)*

2.  **Calculate Slot Position within the Week ($r$):**
    $$r = (t-1) \pmod{16}$$
    *(Value is $0 \dots 15$)*

3.  **Calculate Day within the Week ($d_{local}$):**
    If $r < 15$ (Mon–Fri):
    $$d_{local} = \lfloor \frac{r}{3} \rfloor + 1$$
    If $r = 15$ (Saturday):
    $$d_{local} = 6$$

4.  **Final Day Index ($D_t$):**
    $$D_t = (k \times 6) + d_{local}$$

#### Step B: Assign the Cost
To ensure the solver groups days together, we define the cost $C(t)$ using a **Base Day Penalty** plus a tiny **Tie-Breaker**.

$$C(t) = \underbrace{100 \times D_t}_{\text{Day Penalty}} + \underbrace{\epsilon \times t}_{\text{Tie-Breaker}}$$

* **The Day Penalty ($100 \times D_t$):** We multiply the day index by a large number (like 100). This ensures that slot 3 (Day 1) has a cost of 100, and slot 4 (Day 2) has a cost of 200. This creates the "step" you asked for.
* **The Tie-Breaker ($\epsilon \times t$):** We add a tiny fraction (where $\epsilon$ is small, e.g., 0.1). This ensures that if two exams have equal priority, the solver prefers the morning slot over the afternoon slot, but it never overrides the Day logic.

**Visualizing the Costs:**
| Slot $t$ | Day | Day Calculation | **Cost $C(t)$** |
| :--- | :--- | :--- | :--- |
| **1** (Mon AM) | 1 | $100 \times 1$ | **100.1** |
| **2** (Mon Noon)| 1 | $100 \times 1$ | **100.2** |
| **3** (Mon PM) | 1 | $100 \times 1$ | **100.3** |
| **4** (Tue AM) | 2 | $100 \times 2$ | **200.4** |
| ... | ... | ... | ... |
| **16** (Sat) | 6 | $100 \times 6$ | **601.6** |
| **17** (Mon W2)| 7 | $100 \times 7$ | **701.7** |

---

### 3. Modeling the Priority Weight, $W(P_i)$
You provided a priority range of 0 to 99. You must decide how strictly you want to enforce the "Urgent" exams.

If $P_i = 0$, the penalty is 0, meaning the solver places it randomly. If you want even 0-priority exams to appear as early as possible (after everyone else), add a constant:
$$W(P_i) = P_i^2 + 1$$
