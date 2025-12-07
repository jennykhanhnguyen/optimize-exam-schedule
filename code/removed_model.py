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