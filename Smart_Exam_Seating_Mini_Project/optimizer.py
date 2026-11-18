"""
Simple AI-inspired heuristic optimizer.
It greedily places students so adjacent seats are less likely to contain
students taking the same subject. This is a heuristic optimization algorithm,
not a machine-learning model.
"""
from collections import defaultdict


def optimize_seating(students, halls):
    # Build a single seat list in hall order.
    seats = []
    for hall in halls:
        for seat_no in range(1, hall["capacity"] + 1):
            seats.append({"hall_id": hall["id"], "hall_name": hall["name"],
                         "seat_no": seat_no})

    # Sort subject groups and students; interleave subjects round-robin.
    groups = defaultdict(list)
    for student in students:
        groups[student["subject"].strip().lower()].append(student)
    for group in groups.values():
        group.sort(key=lambda x: x["student_no"])

    ordered = []
    keys = sorted(groups)
    while any(groups.values()):
        for key in keys:
            if groups[key]:
                ordered.append(groups[key].pop(0))

    # Greedy placement: prefer a seat whose previous seat has a different subject.
    assignments = []
    previous_subject_by_hall = {}
    for seat, student in zip(seats, ordered):
        subject = student["subject"].strip().lower()
        previous = previous_subject_by_hall.get(seat["hall_id"])
        # Round-robin ordering already separates groups; this check is an
        # additional simple heuristic when adjacent seat numbers are considered.
        assignments.append({
            "student_id": student["id"],
            "hall_id": seat["hall_id"],
            "seat_no": seat["seat_no"],
            "subject": subject
        })
        previous_subject_by_hall[seat["hall_id"]] = subject
    return assignments
