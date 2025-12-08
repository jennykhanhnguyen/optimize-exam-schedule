# MODEL 2

# model2 = gp.Model("Exam timetabling with room assignment")

# x_allowed = [(e, t) for e in exam_list for t in slot_length if duration[e] <= slot_length[t]]
# y_allowed = [(e, r) for e in exam_list for r in cap if size[e] <= cap[r]]
# x = model2.addVars(x_allowed, vtype=GRB.BINARY, name="x")  # exam <-> timeslot
# y = model2.addVars(y_allowed, vtype=GRB.BINARY, name="y")  # exam <-> room

# 1. Each exam assigned exactly one timeslot
# for s, exams_s in students_exams.items():
#     for t in timeslots:
#         relevant_exams = [e for e in exams_s if (e, t) in x]
#         if len(relevant_exams) > 1:
#             model2.addConstr(
#                 gp.quicksum(x[e, t] for e in relevant_exams) <= 1
#             )


# 2. Each exam assigned exactly one room
# for e in exam_list:
#     allowed_rooms = [r for r in room_list if (e, r) in y_allowed]
#     model2.addConstr(
#         gp.quicksum(y[e, r] for r in allowed_rooms) == 1,
#         name=f"room_once_{e}"
#     )

# 3. No student overlap constraint
# for s, exams_s in students_exams.items():
#     for t in timeslots:
#         # Only include allowed exam-timeslot pairs
#         relevant_exams = [e for e in exams_s if (e, t) in x_allowed]
#         if len(relevant_exams) > 1:
#             model2.addConstr(
#                 gp.quicksum(x[e, t] for e in relevant_exams) <= 1,
#                 name=f"no_overlap_student_{s}_{t}"
#             )

# # 4. Room capacity constraint
# for e in exam_list:
#     for r in room_list:
#         if size[e] > cap[r]:  # cannot fit
#             model2.addConstr(y[e, r] == 0, name=f"cap_forbidden_{e}_{r}")

# # 5. Exam duration must fit slot length
# for e in exam_list:
#     for t in timeslots:
#         if duration[e] > slot_length[t]:
#             model2.addConstr(x[e, t] == 0, name=f"duration_forbidden_{e}_{t}")

# #6. A room cannot host 2 exams in the same slot
# for r in room_list:
#     for t in timeslots:
#         exams_possible = [e for e in exam_list if (e, t) in x and (e, r) in y]
#         if len(exams_possible) > 0:
#             model2.addConstr(
#                 gp.quicksum(x[e, t] * y[e, r] for e in exams_possible) <= 1,
#                 name=f"room_conflict_r{r}_t{t}"
#             )


# Objective = feasibility
# model2.setObjective(0, GRB.MINIMIZE)

# model2.optimize()

# print("Model 2: Exam timetabling with room assignment \n")
# for e in exam_list:
#     assigned_t = [t for t in timeslots if x[e, t].X > 0.5][0]
#     assigned_r = [r for r in room_list if y[e, r].X > 0.5][0]
#     print(f"Exam {e} -> Timeslot {assigned_t}, Room {assigned_r}")


#================================================================

# model3 = gp.Model("Exam timetabling with room merging")

# # define together groups
# together_groups = [
#     ["POPE-A13", "POPE-A14"],
#     ["ART-LECTURE", "ART-SEMINAR"],
#     ["SPORT-LGE1", "SPORT-LGE2"],
# ]

# # Decision variables
# # x[e,t] = 1 if exam e is scheduled in timeslot t
# x = model3.addVars(exam_list, timeslots, vtype=GRB.BINARY, name="x")

# # y[e,r] = aggregated room usage (not used for capacity anymore, but kept for reporting)
# y = model3.addVars(exam_list, room_list, vtype=GRB.BINARY, name="y")

# # z[e,t,r] = 1 if exam e uses room r in timeslot t
# z = model3.addVars(exam_list, timeslots, room_list, vtype=GRB.BINARY, name="z")

# # Constraints

# # 1. Each exam must be assigned exactly one timeslot
# for e in exam_list:
#     model3.addConstr(
#         gp.quicksum(x[e, t] for t in timeslots) == 1, name=f"timeslot_once_{e}"
#     )

# # 2. Linking constraint: z[e,t,r] <= x[e,t]
# for e in exam_list:
#     for t in timeslots:
#         for r in room_list:
#             model3.addConstr(z[e, t, r] <= x[e, t], name=f"link_zx_{e}_{t}_{r}")

# # 3. Aggregate y = SUM_t z
# for e in exam_list:
#     for r in room_list:
#         model3.addConstr(
#             y[e, r] == gp.quicksum(z[e, t, r] for t in timeslots),
#             name=f"aggregate_y_{e}_{r}",
#         )

# # 4. No student may have overlapping exams
# for s, exams_s in students_exams.items():
#     for t in timeslots:
#         for i in range(len(exams_s)):
#             for j in range(i + 1, len(exams_s)):
#                 e1, e2 = exams_s[i], exams_s[j]
#                 model3.addConstr(
#                     x[e1, t] + x[e2, t] <= 1, name=f"no_overlap_{s}_{e1}_{e2}_{t}"
#                 )

# # 5. NEW CAPACITY CONSTRAINT: multi-room allowed
# for e in exam_list:
#     for t in timeslots:
#         model3.addConstr(
#             gp.quicksum(cap[r] * z[e, t, r] for r in room_list) >= size[e] * x[e, t],
#             name=f"capacity_fixed_{e}_{t}",
#         )

# # 6. Duration feasibility
# for e in exam_list:
#     for t in timeslots:
#         if duration[e] > slot_length[t]:
#             model3.addConstr(x[e, t] == 0, name=f"duration_forbidden_{e}_{t}")

# # 7. Room conflict: a room can host at most one exam per timeslot
# for r in room_list:
#     for t in timeslots:
#         model3.addConstr(
#             gp.quicksum(z[e, t, r] for e in exam_list) <= 1,
#             name=f"room_conflict_{r}_{t}",
#         )

# # 8. Together-group constraints
# for group in together_groups:
#     base_room = group[0]
#     for r in group[1:]:
#         for e in exam_list:
#             for t in timeslots:
#                 model3.addConstr(
#                     z[e, t, base_room] == z[e, t, r],
#                     name=f"together_{e}_{t}_{base_room}_{r}",
#                 )

# # Objective
# model3.setObjective(0, GRB.MINIMIZE)

# # Optimize
# model3.optimize()

# print("Model 3: Exam timetabling with room merging (updated)")
# for e in exam_list:
#     assigned_t = [t for t in timeslots if x[e, t].X > 0.5][0]
#     assigned_rooms = [r for r in room_list if y[e, r].X > 0.5]
#     print(f"Exam {e}: Timeslot {assigned_t}, Rooms {assigned_rooms}")


# model3 = gp.Model("Exam_timetabling_integer_split")

# # -----------------------------
# # PRE-PROCESSING: Identify which exams can be split
# # -----------------------------
# SPLIT_THRESHOLD = 480
# large_exams = [e for e in exam_list if size[e] > SPLIT_THRESHOLD]
# small_exams = [e for e in exam_list if size[e] <= SPLIT_THRESHOLD]

# print(f"Exam classification:")
# print(f"  Large exams (>{SPLIT_THRESHOLD}, can split): {len(large_exams)}")
# print(f"  Small exams (≤{SPLIT_THRESHOLD}, must be whole): {len(small_exams)}")
# print()

# # -----------------------------
# # PRE-PROCESSING: Filter impossible room assignments
# # -----------------------------
# print("Pre-processing: Filtering invalid room-exam combinations...")
# min_useful_fraction = 0.05

# valid_z_vars = []
# for e in exam_list:
#     for t in timeslots:
#         # Skip if duration doesn't fit
#         if duration[e] > slot_length[t]:
#             continue
#         for r in room_list:
#             # Only create z variable if room can hold meaningful portion
#             if cap[r] >= size[e] * min_useful_fraction:
#                 valid_z_vars.append((e, t, r))

# print(f"  Total possible (exam, timeslot, room) combinations: {len(exam_list) * len(timeslots) * len(room_list)}")
# print(f"  Valid combinations after filtering: {len(valid_z_vars)}")
# print(f"  Reduction: {100 * (1 - len(valid_z_vars) / (len(exam_list) * len(timeslots) * len(room_list))):.1f}%\n")

# # -----------------------------
# # Decision variables
# # -----------------------------
# # For small exams: binary (0 or 1) - must be whole
# # For large exams: integer (number of students) - can be split
# x = {}
# for e in small_exams:
#     for t in timeslots:
#         x[e, t] = model3.addVar(vtype=GRB.BINARY, name=f"x_{e}_{t}")
# for e in large_exams:
#     for t in timeslots:
#         x[e, t] = model3.addVar(vtype=GRB.INTEGER, lb=0, ub=size[e], name=f"x_{e}_{t}")

# # z[e,t,r] = number of students of exam e in room r at timeslot t
# z = model3.addVars(valid_z_vars, vtype=GRB.INTEGER, lb=0, name="z")

# # y[e,t,g] = 1 if exam e uses super-room g at timeslot t
# y = model3.addVars(exam_list, timeslots, super_rooms, vtype=GRB.BINARY, name="y")

# # Penalty variables
# timeslot_split_penalty = model3.addVars(exam_list, vtype=GRB.INTEGER, name="timeslot_splits")
# room_split_penalty = model3.addVars(exam_list, timeslots, vtype=GRB.INTEGER, name="room_splits")

# # Binary indicator: is room r used by exam e in timeslot t?
# room_used = model3.addVars(valid_z_vars, vtype=GRB.BINARY, name="room_used")

# # Binary indicator for timeslot usage
# w = model3.addVars(exam_list, timeslots, vtype=GRB.BINARY, name="w")

# # -----------------------------
# # Helper: allowed pairs from coincidence groups
# allowed_pairs = set()
# for exam_list_g in groups.values():
#     for i in range(len(exam_list_g)):
#         for j in range(i + 1, len(exam_list_g)):
#             allowed_pairs.add((exam_list_g[i], exam_list_g[j]))
#             allowed_pairs.add((exam_list_g[j], exam_list_g[i]))

# # -----------------------------
# # Pre-build lookups for efficient constraint building
# # -----------------------------
# print("Building lookup tables...")

# # For constraint 5: room_time -> exams
# room_time_to_exams = {}
# for e, t, r in valid_z_vars:
#     if (r, t) not in room_time_to_exams:
#         room_time_to_exams[(r, t)] = []
#     room_time_to_exams[(r, t)].append(e)

# # For constraint 6 & 10: exam_time -> rooms
# exam_time_to_rooms = {}
# for e, t, r in valid_z_vars:
#     if (e, t) not in exam_time_to_rooms:
#         exam_time_to_rooms[(e, t)] = []
#     exam_time_to_rooms[(e, t)].append(r)

# # For constraint 7: room -> super-rooms
# room_to_supers = {}
# for g in super_rooms:
#     for r in super_to_rooms[g]:
#         if r not in room_to_supers:
#             room_to_supers[r] = []
#         room_to_supers[r].append(g)

# super_to_valid_combos = {g: [] for g in super_rooms}
# for e, t, r in valid_z_vars:
#     if r in room_to_supers:
#         for g in room_to_supers[r]:
#             super_to_valid_combos[g].append((e, t, r))

# print("✓ Lookup tables built\n")

# # -----------------------------
# # CONSTRAINTS
# # -----------------------------
# print("Adding constraints...")

# # 1. Each exam fully scheduled
# print("  [1/10] Each exam fully scheduled...", end=" ", flush=True)
# for e in small_exams:
#     # Small exams: sum of binary variables = 1
#     model3.addConstr(gp.quicksum(x[e, t] for t in timeslots) == 1, name=f"full_schedule_{e}")
# for e in large_exams:
#     # Large exams: sum of student counts = total students
#     model3.addConstr(gp.quicksum(x[e, t] for t in timeslots) == size[e], name=f"full_schedule_{e}")
# print(f"✓ ({len(exam_list)} constraints)")

# # 2. Student conflict: students can't be in two places at once
# print("  [2/10] Student conflict constraints...", end=" ", flush=True)
# conflict_count = 0
# for s, exams_s in students_exams.items():
#     for i in range(len(exams_s)):
#         for j in range(i + 1, len(exams_s)):
#             e1, e2 = exams_s[i], exams_s[j]
#             if (e1, e2) in allowed_pairs:
#                 continue
#             for t in timeslots:
#                 # Both small: binary sum ≤ 1
#                 if e1 in small_exams and e2 in small_exams:
#                     model3.addConstr(x[e1, t] + x[e2, t] <= 1, name=f"no_overlap_{s}_{e1}_{e2}_{t}")
#                 # At least one large: can't both be scheduled in same timeslot
#                 else:
#                     model3.addConstr(w[e1, t] + w[e2, t] <= 1, name=f"no_overlap_{s}_{e1}_{e2}_{t}")
#                 conflict_count += 1
# print(f"✓ ({conflict_count} constraints)")

# # 3. Duration feasibility
# print("  [3/10] Duration feasibility...", end=" ", flush=True)
# duration_count = 0
# for e in exam_list:
#     for t in timeslots:
#         if duration[e] > slot_length[t]:
#             model3.addConstr(x[e, t] == 0, name=f"forbidden_duration_{e}_{t}")
#             duration_count += 1
# print(f"✓ ({duration_count} constraints)")

# # 4. Linking to rooms/super-rooms and timeslot activation
# print("  [4/10] Linking exams to rooms...", end=" ", flush=True)
# link_count = 0
# M = max(size[e] for e in exam_list)  # Big-M for linearization

# for e, t, r in valid_z_vars:
#     # z can only be positive if exam is scheduled in this timeslot
#     model3.addConstr(z[e, t, r] <= M * w[e, t], name=f"link_zw_{e}_{t}_{r}")
#     # Link z to room_used indicator
#     model3.addConstr(z[e, t, r] <= M * room_used[e, t, r], name=f"link_room_used_{e}_{t}_{r}")
#     model3.addConstr(z[e, t, r] >= room_used[e, t, r], name=f"force_room_used_{e}_{t}_{r}")
#     link_count += 3

# for e in exam_list:
#     for t in timeslots:
#         # Link w (timeslot usage) to x
#         if e in small_exams:
#             model3.addConstr(w[e, t] == x[e, t], name=f"link_wx_{e}_{t}")
#         else:  # Large exam
#             model3.addConstr(x[e, t] <= M * w[e, t], name=f"link_wx_{e}_{t}")
#             model3.addConstr(x[e, t] >= w[e, t], name=f"force_wx_{e}_{t}")
#             link_count += 1
#         link_count += 1
        
#         # Link y (super-room usage) to w
#         for g in super_rooms:
#             model3.addConstr(y[e, t, g] <= w[e, t], name=f"link_yx_{e}_{t}_{g}")
#             link_count += 1
# print(f"✓ ({link_count} constraints)")

# # 5. Room capacity constraints
# print("  [5/10] Room capacity constraints...", end=" ", flush=True)
# capacity_count = 0
# for (r, t), exams_for_rt in room_time_to_exams.items():
#     model3.addConstr(
#         gp.quicksum(z[e, t, r] for e in exams_for_rt) <= cap[r], 
#         name=f"room_capacity_{r}_{t}"
#     )
#     capacity_count += 1

# for g in super_rooms:
#     for t in timeslots:
#         # Super-room capacity is sum of contributing rooms
#         model3.addConstr(
#             gp.quicksum(size[e] * y[e, t, g] for e in exam_list) <= super_capacity[g], 
#             name=f"superroom_capacity_{g}_{t}"
#         )
#         capacity_count += 1
# print(f"✓ ({capacity_count} constraints)")

# # 6. Ensure exam gets enough capacity
# print("  [6/10] Exam capacity requirements...", end=" ", flush=True)
# exam_capacity_count = 0
# for e in exam_list:
#     for t in timeslots:
#         rooms_for_et = exam_time_to_rooms.get((e, t), [])
#         if e in small_exams:
#             # Small exam: if scheduled here (x=1), must fit in rooms
#             model3.addConstr(
#                 gp.quicksum(z[e, t, r] for r in rooms_for_et) + 
#                 gp.quicksum(super_capacity[g] * y[e, t, g] for g in super_rooms) 
#                 >= size[e] * x[e, t],
#                 name=f"capacity_per_exam_{e}_{t}"
#             )
#         else:
#             # Large exam: students scheduled here must fit in rooms
#             model3.addConstr(
#                 gp.quicksum(z[e, t, r] for r in rooms_for_et) + 
#                 gp.quicksum(super_capacity[g] * y[e, t, g] for g in super_rooms) 
#                 >= x[e, t],
#                 name=f"capacity_per_exam_{e}_{t}"
#             )
#         exam_capacity_count += 1
# print(f"✓ ({exam_capacity_count} constraints)")

# # 7. Super-room blocks internal rooms
# print("  [7/10] Super-room blocking...", end=" ", flush=True)
# blocking_count = 0
# for g, valid_combos in super_to_valid_combos.items():
#     for e, t, r in valid_combos:
#         model3.addConstr(room_used[e, t, r] >= y[e, t, g], name=f"superroom_block_{e}_{t}_{g}_{r}")
#         blocking_count += 1
# print(f"✓ ({blocking_count} constraints)")

# # 8. Coincidence groups: same timeslot
# print("  [8/10] Coincidence constraints...", end=" ", flush=True)
# coincidence_count = 0
# for g, exam_list_g in groups.items():
#     if len(exam_list_g) <= 1:
#         continue
#     leader = exam_list_g[0]
#     for e in exam_list_g[1:]:
#         for t in timeslots:
#             model3.addConstr(w[e, t] == w[leader, t], name=f"coincide_timeslot_{g}_{e}_{t}")
#             model3.addConstr(x[e, t] == x[leader, t], name=f"coincide_fraction_{g}_{e}_{t}")
#             coincidence_count += 2
# print(f"✓ ({coincidence_count} constraints)")

# # 9. Small exams must use single room (or single super-room)
# print("  [9/10] Small exams single-room constraint...", end=" ", flush=True)
# single_room_count = 0
# for e in small_exams:
#     for t in timeslots:
#         rooms_for_et = exam_time_to_rooms.get((e, t), [])
#         if rooms_for_et:
#             # Total rooms + super-rooms used ≤ 1
#             model3.addConstr(
#                 gp.quicksum(room_used[e, t, r] for r in rooms_for_et) +
#                 gp.quicksum(y[e, t, g] for g in super_rooms) <= 1,
#                 name=f"single_room_{e}_{t}"
#             )
#             single_room_count += 1
# print(f"✓ ({single_room_count} constraints)")

# # 10. Timeslot and room split penalties (only for large exams)
# print("  [10/10] Split penalties...", end=" ", flush=True)
# penalty_count = 0

# # Timeslot split penalty
# for e in large_exams:
#     model3.addConstr(
#         timeslot_split_penalty[e] >= gp.quicksum(w[e, t] for t in timeslots) - 1,
#         name=f"timeslot_penalty_{e}"
#     )
#     penalty_count += 1

# for e in small_exams:
#     model3.addConstr(timeslot_split_penalty[e] == 0, name=f"no_timeslot_penalty_{e}")
#     penalty_count += 1

# # Room split penalty (only matters for large exams)
# for e in large_exams:
#     for t in timeslots:
#         rooms_for_et = exam_time_to_rooms.get((e, t), [])
#         if rooms_for_et:
#             num_rooms_used = gp.quicksum(room_used[e, t, r] for r in rooms_for_et)
#             super_used = gp.quicksum(y[e, t, g] for g in super_rooms)
#             model3.addConstr(
#                 room_split_penalty[e, t] >= num_rooms_used - 1 - super_used,
#                 name=f"room_penalty_{e}_{t}"
#             )
#             penalty_count += 1

# for e in small_exams:
#     for t in timeslots:
#         model3.addConstr(room_split_penalty[e, t] == 0, name=f"no_room_penalty_{e}_{t}")
#         penalty_count += 1

# print(f"✓ ({penalty_count} constraints)")

# print(f"\nTotal constraints added: {model3.NumConstrs}")
# print(f"Total variables: {model3.NumVars} ({model3.NumBinVars} binary, {model3.NumIntVars} integer)")
# print()

# # -----------------------------
# # Objective: minimize splits (only penalize large exams)
# model3.setObjective(
#     100 * gp.quicksum(timeslot_split_penalty[e] for e in large_exams) +
#     gp.quicksum(room_split_penalty[e, t] for e in large_exams for t in timeslots),
#     GRB.MINIMIZE
# )

# # -----------------------------
# # Solve with performance tuning
# print("Starting optimization...\n")
# model3.Params.MIPGap = 0.01
# model3.Params.TimeLimit = 180
# model3.Params.MIPFocus = 1
# model3.Params.Heuristics = 0.3
# model3.Params.Presolve = 2

# model3.optimize()

# # -----------------------------
# # Retrieve results
# print("\n" + "="*80)
# if model3.status == GRB.OPTIMAL:
#     print("✓ OPTIMAL SOLUTION FOUND")
# elif model3.status == GRB.TIME_LIMIT:
#     print("⏱️  TIME LIMIT REACHED - BEST SOLUTION SO FAR")
# else:
#     print(f"❌ OPTIMIZATION FAILED - Status: {model3.status}")
#     exit()

# print("="*80)

# total_timeslot_penalty = 0
# total_room_penalty = 0

# for e in exam_list:
#     timeslots_used = [(t, x[e, t].X) for t in timeslots if x[e, t].X > 0.5]
    
#     if len(timeslots_used) > 0:
#         print(f"\n{'─'*80}")
#         exam_type = "LARGE" if e in large_exams else "SMALL"
#         print(f"Exam: {e} ({exam_type}, Total students: {size[e]})")
#         print(f"{'─'*80}")
        
#         exam_room_penalty = 0
#         for t, student_count in timeslots_used:
#             used_rooms = [(r, z[e, t, r].X) for r in room_list if (e, t, r) in valid_z_vars and z[e, t, r].X > 0.5]
#             used_super = [g for g in super_rooms if y[e, t, g].X > 0.5]
#             room_penalty_here = room_split_penalty[e, t].X
#             exam_room_penalty += room_penalty_here
            
#             if e in small_exams:
#                 print(f"  📅 Timeslot {t}: ALL {int(student_count)} students")
#             else:
#                 print(f"  📅 Timeslot {t}: {int(student_count)} students")
            
#             print(f"     🏢 Rooms used: {len(used_rooms)}")
#             for r, z_val in used_rooms:
#                 print(f"        • {r}: {int(z_val)} students")
#             if used_super:
#                 print(f"     🏟️  Super-rooms: {used_super}")
#             if e in large_exams:
#                 print(f"     ⚠️  Room split penalty: {room_penalty_here:.0f}")
        
#         ts_penalty = timeslot_split_penalty[e].X
#         total_timeslot_penalty += ts_penalty
#         total_room_penalty += exam_room_penalty
        
#         if e in large_exams:
#             print(f"\n  📊 Penalties for {e}:")
#             print(f"     • Timeslot splits: {ts_penalty:.0f} (used {len(timeslots_used)} timeslot(s))")
#             print(f"     • Room splits (total): {exam_room_penalty:.0f}")

# print(f"\n{'═'*80}")
# print(f"OVERALL SUMMARY")
# print(f"{'═'*80}")
# print(f"  Total Timeslot Split Penalty: {total_timeslot_penalty:.0f}")
# print(f"  Total Room Split Penalty: {total_room_penalty:.0f}")
# print(f"  Weighted Objective Value: {model3.ObjVal:.2f}")
# print(f"  Solution time: {model3.Runtime:.2f} seconds")
# print(f"  MIP Gap: {model3.MIPGap*100:.2f}%")
# print(f"{'═'*80}")

# model3 = gp.Model("Exam_timetabling_timeslot_split")

# # -----------------------------
# # PRE-PROCESSING: Filter impossible room assignments
# # -----------------------------
# print("Pre-processing: Filtering invalid room-exam combinations...")
# min_useful_fraction = 0.05  # Room must hold at least 5% of exam

# valid_z_vars = []
# for e in exam_list:
#     for t in timeslots:
#         # Skip if duration doesn't fit
#         if duration[e] > slot_length[t]:
#             continue
#         for r in room_list:
#             # Only create z variable if room can hold meaningful portion
#             if cap[r] >= size[e] * min_useful_fraction:
#                 valid_z_vars.append((e, t, r))

# print(f"  Total possible (exam, timeslot, room) combinations: {len(exam_list) * len(timeslots) * len(room_list)}")
# print(f"  Valid combinations after filtering: {len(valid_z_vars)}")
# print(f"  Reduction: {100 * (1 - len(valid_z_vars) / (len(exam_list) * len(timeslots) * len(room_list))):.1f}%\n")

# # -----------------------------
# # Decision variables
# # -----------------------------
# x = model3.addVars(exam_list, timeslots, vtype=GRB.CONTINUOUS, lb=0, ub=1, name="x")
# z = model3.addVars(valid_z_vars, vtype=GRB.CONTINUOUS, lb=0, ub=1, name="z")
# y = model3.addVars(exam_list, timeslots, super_rooms, vtype=GRB.BINARY, name="y")

# # Penalty variables
# timeslot_split_penalty = model3.addVars(exam_list, vtype=GRB.INTEGER, name="timeslot_splits")
# room_split_penalty = model3.addVars(exam_list, timeslots, vtype=GRB.CONTINUOUS, name="room_splits")

# # Binary indicator: is room r used by exam e in timeslot t?
# room_used = model3.addVars(valid_z_vars, vtype=GRB.BINARY, name="room_used")

# # Binary indicator for timeslot usage (for coincidence constraints)
# w = model3.addVars(exam_list, timeslots, vtype=GRB.BINARY, name="w")

# # -----------------------------
# # Helper: allowed pairs from coincidence groups
# allowed_pairs = set()
# for exam_list_g in groups.values():
#     for i in range(len(exam_list_g)):
#         for j in range(i + 1, len(exam_list_g)):
#             allowed_pairs.add((exam_list_g[i], exam_list_g[j]))
#             allowed_pairs.add((exam_list_g[j], exam_list_g[i]))

# # -----------------------------
# # 1. Each exam fully scheduled (sum of fractions = 1)
# print("Adding constraints...")
# print("  [1/10] Each exam fully scheduled...", end=" ", flush=True)
# for e in exam_list:
#     model3.addConstr(gp.quicksum(x[e, t] for t in timeslots) == 1, name=f"full_schedule_{e}")
# print(f"✓ ({len(exam_list)} constraints)")

# # 2. Student conflict: students can't be in two places at once
# print("  [2/10] Student conflict constraints...", end=" ", flush=True)
# conflict_count = 0
# for s, exams_s in students_exams.items():
#     for i in range(len(exams_s)):
#         for j in range(i + 1, len(exams_s)):
#             e1, e2 = exams_s[i], exams_s[j]
#             if (e1, e2) in allowed_pairs:
#                 continue
#             for t in timeslots:
#                 model3.addConstr(x[e1, t] + x[e2, t] <= 1, name=f"no_overlap_{s}_{e1}_{e2}_{t}")
#                 conflict_count += 1
# print(f"✓ ({conflict_count} constraints)")

# # 3. Duration feasibility (already filtered in valid_z_vars, but enforce for x too)
# print("  [3/10] Duration feasibility...", end=" ", flush=True)
# duration_count = 0
# for e in exam_list:
#     for t in timeslots:
#         if duration[e] > slot_length[t]:
#             model3.addConstr(x[e, t] == 0, name=f"forbidden_duration_{e}_{t}")
#             duration_count += 1
# print(f"✓ ({duration_count} constraints)")

# # -----------------------------
# # 4. Linking to rooms/super-rooms
# print("  [4/10] Linking exams to rooms...", end=" ", flush=True)
# link_count = 0
# for e, t, r in valid_z_vars:
#     model3.addConstr(z[e, t, r] <= x[e, t], name=f"link_zx_{e}_{t}_{r}")
#     model3.addConstr(z[e, t, r] <= room_used[e, t, r], name=f"link_room_used_{e}_{t}_{r}")
#     link_count += 2

# for e in exam_list:
#     for t in timeslots:
#         for g in super_rooms:
#             model3.addConstr(y[e, t, g] <= x[e, t], name=f"link_yx_{e}_{t}_{g}")
#             link_count += 1
# print(f"✓ ({link_count} constraints)")

# # 5. Room capacity constraints
# print("  [5/10] Room capacity constraints...", end=" ", flush=True)
# capacity_count = 0

# # Pre-build a lookup: for each (r, t), which exams have valid z variables?
# room_time_to_exams = {}
# for e, t, r in valid_z_vars:
#     if (r, t) not in room_time_to_exams:
#         room_time_to_exams[(r, t)] = []
#     room_time_to_exams[(r, t)].append(e)

# # Now add constraints only for (r, t) pairs that have valid exams
# for (r, t), exams_for_rt in room_time_to_exams.items():
#     model3.addConstr(
#         gp.quicksum(size[e] * z[e, t, r] for e in exams_for_rt) <= cap[r], 
#         name=f"room_capacity_{r}_{t}"
#     )
#     capacity_count += 1

# for g in super_rooms:
#     for t in timeslots:
#         model3.addConstr(
#             gp.quicksum(size[e] * y[e, t, g] for e in exam_list) <= super_capacity[g], 
#             name=f"superroom_capacity_{g}_{t}"
#         )
#         capacity_count += 1
# print(f"✓ ({capacity_count} constraints)")

# # 6. Ensure exam fraction gets enough capacity
# print("  [6/10] Exam capacity requirements...", end=" ", flush=True)
# exam_capacity_count = 0

# # Pre-build lookup: for each (e, t), which rooms have valid z variables?
# exam_time_to_rooms = {}
# for e, t, r in valid_z_vars:
#     if (e, t) not in exam_time_to_rooms:
#         exam_time_to_rooms[(e, t)] = []
#     exam_time_to_rooms[(e, t)].append(r)

# for e in exam_list:
#     for t in timeslots:
#         rooms_for_et = exam_time_to_rooms.get((e, t), [])
#         model3.addConstr(
#             gp.quicksum(cap[r] * z[e, t, r] for r in rooms_for_et) + 
#             gp.quicksum(super_capacity[g] * y[e, t, g] for g in super_rooms) 
#             >= size[e] * x[e, t],
#             name=f"capacity_per_exam_{e}_{t}"
#         )
#         exam_capacity_count += 1
# print(f"✓ ({exam_capacity_count} constraints)")

# # 7. Super-room blocks internal rooms
# print("  [7/10] Super-room blocking...", end=" ", flush=True)
# blocking_count = 0

# # Pre-build lookup: for each super-room g, which (e, t, r) combinations are valid?
# # Build room-to-superroom mapping first
# room_to_supers = {}
# for g in super_rooms:
#     for r in super_to_rooms[g]:
#         if r not in room_to_supers:
#             room_to_supers[r] = []
#         room_to_supers[r].append(g)

# # Now iterate through valid_z_vars once and categorize by super-room
# super_to_valid_combos = {g: [] for g in super_rooms}
# for e, t, r in valid_z_vars:
#     if r in room_to_supers:
#         for g in room_to_supers[r]:
#             super_to_valid_combos[g].append((e, t, r))

# # Add constraints only for valid combinations
# for g, valid_combos in super_to_valid_combos.items():
#     for e, t, r in valid_combos:
#         model3.addConstr(z[e, t, r] >= y[e, t, g], name=f"superroom_block_{e}_{t}_{g}_{r}")
#         blocking_count += 1
# print(f"✓ ({blocking_count} constraints)")

# # -----------------------------
# # 8. Coincidence groups: same timeslot
# print("  [8/10] Timeslot activation & coincidence...", end=" ", flush=True)
# coincidence_count = 0
# for e in exam_list:
#     for t in timeslots:
#         model3.addConstr(x[e, t] <= w[e, t], name=f"activate_w_{e}_{t}")
#         model3.addConstr(x[e, t] >= 0.001 * w[e, t], name=f"force_w_{e}_{t}")
#         coincidence_count += 2

# for g, exam_list_g in groups.items():
#     if len(exam_list_g) <= 1:
#         continue
#     leader = exam_list_g[0]
#     for e in exam_list_g[1:]:
#         for t in timeslots:
#             model3.addConstr(w[e, t] == w[leader, t], name=f"coincide_timeslot_{g}_{e}_{t}")
#             model3.addConstr(x[e, t] == x[leader, t], name=f"coincide_fraction_{g}_{e}_{t}")
#             coincidence_count += 2
# print(f"✓ ({coincidence_count} constraints)")

# # -----------------------------
# # 9. Timeslot split penalty
# print("  [9/10] Timeslot split penalties...", end=" ", flush=True)
# ts_penalty_count = 0
# for e in exam_list:
#     model3.addConstr(
#         timeslot_split_penalty[e] >= gp.quicksum(w[e, t] for t in timeslots) - 1,
#         name=f"timeslot_penalty_{e}"
#     )
#     ts_penalty_count += 1
# print(f"✓ ({ts_penalty_count} constraints)")

# # 10. Room split penalty
# print("  [10/10] Room split penalties...", end=" ", flush=True)
# room_penalty_count = 0

# # Pre-build lookup: for each (e, t), which rooms have valid z variables?
# # (We already built this for constraint 6, reuse it!)
# for e in exam_list:
#     for t in timeslots:
#         rooms_for_et = exam_time_to_rooms.get((e, t), [])
#         if rooms_for_et:  # Only add constraint if exam can use rooms in this timeslot
#             num_rooms_used = gp.quicksum(room_used[e, t, r] for r in rooms_for_et)
#             super_used = gp.quicksum(y[e, t, g] for g in super_rooms)
#             model3.addConstr(
#                 room_split_penalty[e, t] >= num_rooms_used - 1 - super_used,
#                 name=f"room_penalty_{e}_{t}"
#             )
#             room_penalty_count += 1
# print(f"✓ ({room_penalty_count} constraints)")

# print(f"\nTotal constraints added: {model3.NumConstrs}")
# print(f"Total variables: {model3.NumVars} ({model3.NumBinVars} binary, {model3.NumIntVars} integer)")
# print()



# # -----------------------------
# # Objective: minimize splits
# model3.setObjective(
#     100 * gp.quicksum(timeslot_split_penalty[e] for e in exam_list) +
#     gp.quicksum(room_split_penalty[e, t] for e in exam_list for t in timeslots),
#     GRB.MINIMIZE
# )

# # -----------------------------
# # Solve with performance tuning
# print("Starting optimization...\n")

# model3.optimize()

# # -----------------------------
# # Retrieve results
# print("\n" + "="*80)
# if model3.status == GRB.OPTIMAL:
#     print("✓ OPTIMAL SOLUTION FOUND")
# elif model3.status == GRB.TIME_LIMIT:
#     print("⏱️  TIME LIMIT REACHED - BEST SOLUTION SO FAR")
# else:
#     print(f"❌ OPTIMIZATION FAILED - Status: {model3.status}")
#     exit()

# print("="*80)

# total_timeslot_penalty = 0
# total_room_penalty = 0

# for e in exam_list:
#     timeslots_used = [(t, x[e, t].X) for t in timeslots if x[e, t].X > 0.01]
    
#     if len(timeslots_used) > 0:
#         print(f"\n{'─'*80}")
#         print(f"Exam: {e} (Total students: {size[e]})")
#         print(f"{'─'*80}")
        
#         exam_room_penalty = 0
#         for t, frac in timeslots_used:
#             used_rooms = [(r, z[e, t, r].X) for r in room_list if (e, t, r) in valid_z_vars and z[e, t, r].X > 0.01]
#             used_super = [g for g in super_rooms if y[e, t, g].X > 0.5]
#             students_here = size[e] * frac
#             room_penalty_here = room_split_penalty[e, t].X
#             exam_room_penalty += room_penalty_here
            
#             print(f"  📅 Timeslot {t}: {frac*100:.1f}% → {students_here:.0f} students")
#             print(f"     🏢 Rooms used: {len(used_rooms)}")
#             for r, z_val in used_rooms:
#                 capacity_used = size[e] * frac * z_val
#                 print(f"        • {r}: {z_val*100:.1f}% allocation → {capacity_used:.0f} students")
#             if used_super:
#                 print(f"     🏟️  Super-rooms: {used_super}")
#             print(f"     ⚠️  Room split penalty: {room_penalty_here:.2f}")
        
#         ts_penalty = timeslot_split_penalty[e].X
#         total_timeslot_penalty += ts_penalty
#         total_room_penalty += exam_room_penalty
        
#         print(f"\n  📊 Penalties for {e}:")
#         print(f"     • Timeslot splits: {ts_penalty:.0f} (used {len(timeslots_used)} timeslot(s))")
#         print(f"     • Room splits (total): {exam_room_penalty:.2f}")

# print(f"\n{'═'*80}")
# print(f"OVERALL SUMMARY")
# print(f"{'═'*80}")
# print(f"  Total Timeslot Split Penalty: {total_timeslot_penalty:.0f}")
# print(f"  Total Room Split Penalty: {total_room_penalty:.2f}")
# print(f"  Weighted Objective Value: {model3.ObjVal:.2f}")
# print(f"     (100 × timeslot_penalty + room_penalty)")
# print(f"     = 100 × {total_timeslot_penalty:.0f} + {total_room_penalty:.2f}")
# print(f"     = {100*total_timeslot_penalty + total_room_penalty:.2f}")
# print(f"  Solution time: {model3.Runtime:.2f} seconds")
# print(f"  MIP Gap: {model3.MIPGap*100:.2f}%")
# print(f"{'═'*80}")