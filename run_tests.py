from VIBE import load_records, make_student, save_records, display_students, class_stats, search_student, DATA_FILE

students = load_records(DATA_FILE)

# Add two students
s1 = make_student('Alice Smith', 'A001', [85, 90, 95])
students.append(s1)

s2 = make_student('Bob Jones', 'B002', [78, 82, 88])
students.append(s2)

print('--- After Adding ---')
display_students(students)

print('\n--- Class Stats ---')
class_stats(students)

print('\n--- Search for Alice ---')
search_student(students, 'Alice')

print('\n--- Saving Records ---')
save_records(DATA_FILE, students)
