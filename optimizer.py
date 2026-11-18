
import heapq
from collections import defaultdict


def optimize_seating(students, halls):
    """
    Greedy AI-inspired optimization:
    Places students taking different subjects in consecutive seats
    whenever possible.
    """

    assignments = []
    remaining_students = sorted(
        students, key=lambda s: str(s["student_no"])
    )

    for hall in halls:
        capacity = hall["capacity"]

        # Select students for this hall
        hall_students = remaining_students[:capacity]
        remaining_students = remaining_students[capacity:]

        # Group students by subject
        groups = defaultdict(list)

        for student in hall_students:
            subject = student["subject"].strip().lower()
            groups[subject].append(student)

        # Create a max heap based on remaining subject counts
        heap = []

        for subject, group in groups.items():
            heapq.heappush(heap, (-len(group), subject))

        previous_subject = None
        seat_no = 1

        while heap:
            first = heapq.heappop(heap)

            # Avoid repeating the previous subject
            if first[1] == previous_subject and heap:
                second = heapq.heappop(heap)
                heapq.heappush(heap, first)
                chosen = second
            else:
                chosen = first

            subject = chosen[1]
            student = groups[subject].pop(0)

            assignments.append({
                "student_id": student["id"],
                "hall_id": hall["id"],
                "seat_no": seat_no,
                "subject": student["subject"]
            })

            previous_subject = subject
            seat_no += 1

            # Add the subject back if students remain
            if groups[subject]:
                heapq.heappush(
                    heap,
                    (-len(groups[subject]), subject)
                )

    return assignments


def calculate_conflicts(assignments):
    """
    Count consecutive same-subject seats within each hall.
    Lower score means a better arrangement.
    """

    hall_seats = defaultdict(list)

    for item in assignments:
        hall_seats[item["hall_id"]].append(item)

    total_conflicts = 0

    for hall_id, seats in hall_seats.items():
        seats.sort(key=lambda x: x["seat_no"])

        for i in range(len(seats) - 1):
            if (seats[i]["subject"].strip().lower()
                    == seats[i + 1]["subject"].strip().lower()):
                total_conflicts += 1

    return total_conflicts
