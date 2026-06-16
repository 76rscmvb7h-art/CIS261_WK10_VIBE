# Emmanuel Cowden
# CIS261
# VIBE Coding - Student Grade Manager

import os
import sys

DATA_FILE = "student_grades.txt"
NUM_TESTS = 3

def calculate_average(*tests: float) -> float:
	vals = [float(x) for x in tests]
	if not vals:
		return 0.0
	return round(sum(vals) / len(vals), 2)


def calculate_grade(avg: float) -> str:
	if avg >= 90:
		return 'A'
	if avg >= 80:
		return 'B'
	if avg >= 70:
		return 'C'
	if avg >= 60:
		return 'D'
	return 'F'


def make_student(name: str, sid: str, tests: list) -> dict:
	tests_f = [round(float(x), 2) for x in tests]
	avg = calculate_average(*tests_f)
	grade = calculate_grade(avg)
	student = {
		'name': name.strip(),
		'id': sid.strip(),
		'tests': tests_f,
		'average': avg,
		'grade': grade,
	}
	# For backward compatibility, also set test1..testN keys for display
	for i, t in enumerate(tests_f, start=1):
		student[f'test{i}'] = t
	return student


def to_line(student: dict) -> str:
	# name|id|t1|t2|...|tN|average|grade
	tests = student.get('tests') or [student.get(f'test{i+1}', 0.0) for i in range(NUM_TESTS)]
	tests_str = '|'.join(f"{t:.2f}" for t in tests)
	return f"{student['name']}|{student['id']}|{tests_str}|{student['average']:.2f}|{student['grade']}"


def from_line(line: str) -> dict:
	parts = [p.strip() for p in line.strip().split('|')]
	if not parts:
		raise ValueError("Empty line")
	# If this is a NUMTESTS header, caller should handle it before calling from_line
	if parts[0].upper().startswith('NUMTESTS'):
		raise ValueError('Header line')
	# last two parts are average and grade
	if len(parts) < 4:
		raise ValueError('Invalid record format')
	name, sid = parts[0], parts[1]
	# tests are parts[2:-2]
	tests_parts = parts[2:-2]
	tests = [float(x) for x in tests_parts]
	return make_student(name, sid, tests)


def load_records(filename: str) -> list:
	students = []
	if not os.path.exists(filename):
		return students
	try:
		with open(filename, 'r', encoding='utf-8') as f:
			global NUM_TESTS
			first = True
			header_found = False
			for line in f:
				line = line.strip()
				if not line:
					continue
				# detect header like NUMTESTS|N
				if first and line.upper().startswith('NUMTESTS|'):
					try:
						_, val = line.split('|', 1)
						NUM_TESTS = int(val)
						header_found = True
					except Exception:
						NUM_TESTS = 3
						header_found = True
					first = False
					continue
				first = False
				try:
					student = from_line(line)
					students.append(student)
				except Exception:
					# skip malformed lines but continue loading
					continue
			# if file had no header, infer NUM_TESTS from existing records
			if not header_found and students:
				max_tests = max(len(s.get('tests', [])) for s in students)
				if max_tests > 0:
					NUM_TESTS = max_tests
	except Exception as e:
		print(f"Error loading records: {e}")
	return students


def save_records(filename: str, students: list):
	try:
		with open(filename, 'w', encoding='utf-8') as f:
			# write header with NUMTESTS
			f.write(f"NUMTESTS|{NUM_TESTS}\n")
			for s in students:
				f.write(to_line(s) + '\n')
		print(f"Saved {len(students)} record(s) to {filename}")
	except Exception as e:
		print(f"Error saving records: {e}")


def input_float(prompt: str) -> float:
	while True:
		val = input(prompt).strip()
		if val == '\x1b' or val.upper() == 'ESC':
			return None
		try:
			f = float(val)
			if f > 100:
				print("Score cannot exceed 100. Please enter a valid score.")
				continue
			return round(f, 2)
		except ValueError:
			print("Please enter a valid number (e.g., 87.5). Type ESC to cancel.")


def add_student(students: list):
	print("Enter new student information (type ESC at any prompt to cancel)")
	name = input("Name: ").strip()
	if name == '\x1b' or name.upper() == 'ESC' or not name:
		print("Add cancelled.")
		return
	sid = input("ID: ").strip()
	if sid == '\x1b' or sid.upper() == 'ESC' or not sid:
		print("Add cancelled.")
		return
	if any(s['id'].strip().lower() == sid.strip().lower() for s in students):
		print(f"Duplicate ID detected: {sid}. Each student must have a unique ID.")
		print("Add cancelled.")
		return
	# Ask for number of tests before entering test scores
	global NUM_TESTS
	try:
		print(f"Current number of tests: {NUM_TESTS}")
		resp = input("Enter number of tests or press Enter to use current: ").strip()
		if resp:
			try:
				num_tests = int(resp)
				if num_tests <= 0:
					print("Number must be positive. Using current value.")
					num_tests = NUM_TESTS
				else:
					NUM_TESTS = num_tests
			except ValueError:
				print("Invalid number. Using current value.")
				num_tests = NUM_TESTS
		else:
			num_tests = NUM_TESTS
	except Exception:
		num_tests = NUM_TESTS
	tests = []
	for i in range(1, num_tests + 1):
		val = input_float(f"Test {i} score: ")
		if val is None:
			print("Add cancelled.")
			return
		tests.append(val)
	student = make_student(name, sid, tests)
	# Ask for grade override
	print(f"Calculated average: {student['average']:.2f}")
	grade_input = input("Enter grade (A/B/C/D/F) or press Enter for auto-calculated grade: ").strip().upper()
	if grade_input and grade_input in ('A', 'B', 'C', 'D', 'F'):
		student['grade'] = grade_input
		print(f"Grade set to: {grade_input}")
	# Display summary and ask for confirmation
	print(f"\nStudent Summary:")
	print(f"  Name: {student['name']}")
	print(f"  ID: {student['id']}")
	print(f"  Average: {student['average']:.2f}")
	print(f"  Grade: {student['grade']}")
	confirm = input("\nSave this record? (Y/N): ").strip().upper()
	if confirm != 'Y':
		print("Record not saved.")
		return
	students.append(student)
	save_records(DATA_FILE, students)
	print(f"Added {student['name']} (ID: {student['id']}) Average: {student['average']:.2f} Grade: {student['grade']}")


def adjust_students_for_numtests(new_n: int, students: list):
	global NUM_TESTS
	for s in students:
		tests = s.get('tests', [])
		if len(tests) < new_n:
			tests = tests + [0.0] * (new_n - len(tests))
		elif len(tests) > new_n:
			tests = tests[:new_n]
		# update tests and recalc
		s['tests'] = [round(float(x), 2) for x in tests]
		for i, t in enumerate(s['tests'], start=1):
			s[f'test{i}'] = t
		s['average'] = calculate_average(*s['tests'])
		s['grade'] = calculate_grade(s['average'])
	NUM_TESTS = new_n


def display_students(students: list):
	if not students:
		print("No student records available.")
		return
	# Sort students by last name (alphabetically)
	sorted_students = sorted(students, key=lambda s: s['name'].split()[-1].lower())
	# Build dynamic header based on the maximum number of tests any student has
	max_tests = max(len(s.get('tests', [])) for s in sorted_students)
	if max_tests <= 0:
		max_tests = NUM_TESTS
	tests_headers = ' '.join(f"{'Test'+str(i):>7}" for i in range(1, max_tests + 1))
	header = f"{'Name':<25} {'ID':<10} {tests_headers} {'Avg':>7} {'Grade':>6}"
	print(header)
	print('-' * len(header))
	for s in sorted_students:
		tests = s.get('tests', [])[:max_tests]
		while len(tests) < max_tests:
			tests.append(0.0)
		tests_str = ' '.join(f"{t:7.2f}" for t in tests)
		print(f"{s['name']:<25} {s['id']:<10} {tests_str} {s['average']:7.2f} {s['grade']:>6}")


def class_stats(students: list):
	if not students:
		print("No student records to calculate statistics.")
		return
	averages = [s['average'] for s in students]
	highest = max(averages)
	lowest = min(averages)
	class_avg = round(sum(averages) / len(averages), 2)
	print(f"Highest average: {highest:.2f}")
	print(f"Lowest average:  {lowest:.2f}")
	print(f"Class average:   {class_avg:.2f}")


def search_student(students: list, name: str):
	name = name.strip().lower()
	found = [s for s in students if name in s['name'].lower()]
	if not found:
		print(f"No students found matching '{name}'.")
		return False
	display_students(found)
	return True


def modify_student_score(students: list):
	if not students:
		print('No student records available.')
		return
	print('Current students:')
	display_students(students)
	sid = input('Enter student ID to modify: ').strip()
	if sid == '\x1b' or sid.upper() == 'ESC' or not sid:
		print('Modification cancelled.')
		return
	matches = [s for s in students if s['id'].strip().lower() == sid.strip().lower()]
	if not matches:
		print(f"No student found with ID '{sid}'.")
		return
	student = matches[0]
	print(f"Selected student: {student['name']} (ID: {student['id']})")
	max_tests = 3
	for i in range(1, max_tests + 1):
		value = student.get('tests', [])
		if i <= len(value):
			print(f"Test {i}: {value[i-1]:.2f}")
		else:
			print(f"Test {i}: 0.00")
	while True:
		test_choice = input(f'Enter test number to modify (1-{max_tests}) or ESC to cancel: ').strip()
		if test_choice == '\x1b' or test_choice.upper() == 'ESC' or not test_choice:
			print('Modification cancelled.')
			return
		if not test_choice.isdigit():
			print('Please enter a valid test number.')
			continue
		test_num = int(test_choice)
		if test_num < 1 or test_num > max_tests:
			print(f'Please choose a number between 1 and {max_tests}.')
			continue
		break
	current_tests = student.get('tests', [])[:]
	if len(current_tests) < test_num:
		current_tests.extend([0.0] * (test_num - len(current_tests)))
	new_score = input_float(f'Enter new score for Test {test_num}: ')
	if new_score is None:
		print('Modification cancelled.')
		return
	current_tests[test_num - 1] = new_score
	student['tests'] = [round(float(x), 2) for x in current_tests]
	for i, t in enumerate(student['tests'], start=1):
		student[f'test{i}'] = t
	student['average'] = calculate_average(*student['tests'])
	student['grade'] = calculate_grade(student['average'])
	print(f"Updated Test {test_num} to {new_score:.2f}. New average: {student['average']:.2f}, Grade: {student['grade']}")
	confirm = input('Save changes? (Y/N): ').strip().upper()
	if confirm == 'Y':
		save_records(DATA_FILE, students)
	else:
		print('Changes not saved.')


def delete_student_record(students: list):
	if not students:
		print('No student records available.')
		return
	print('Current students:')
	sorted_students = sorted(students, key=lambda s: s['name'].split()[-1].lower())
	for i, student in enumerate(sorted_students, start=1):
		print(f"{i}. {student['name']} (ID: {student['id']})")
	while True:
		choice = input('Enter student number to delete or ESC to cancel: ').strip()
		if choice == '\x1b' or choice.upper() == 'ESC' or not choice:
			print('Delete cancelled.')
			return
		if not choice.isdigit():
			print('Please enter a valid student number.')
			continue
		choice_num = int(choice)
		if choice_num < 1 or choice_num > len(sorted_students):
			print(f'Please choose a number between 1 and {len(sorted_students)}.')
			continue
		break
	student = sorted_students[choice_num - 1]
	print(f"Selected student: {student['name']} (ID: {student['id']})")
	confirm = input('Are you sure you want to delete this student record? (Y/N): ').strip().upper()
	if confirm != 'Y':
		print('Delete cancelled.')
		return
	students.remove(student)
	save_records(DATA_FILE, students)
	print(f"Deleted student record for {student['name']} (ID: {student['id']}).")


def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')


def print_welcome_banner():
	print("="*50)
	print("Welcome to the Student Calculator".center(50))
	print("="*50)


def print_closing_banner():
	print("="*50)
	print("Have a Good Day".center(50))
	print("="*50)


def print_section_heading(title: str):
	print('=' * 50)
	print(title.center(50))
	print('=' * 50)


def main():
	global NUM_TESTS
	print_welcome_banner()
	students = load_records(DATA_FILE)
	print(f"Loaded {len(students)} record(s) from {DATA_FILE}.")

	while True:
		print()
		print_section_heading('Student Records Manager')
		print('1) Add New Student')
		print('2) Display All Students')
		print('3) Modify Student Score')
		print('4) Class Statistics')
		print('5) Search By Name')
		print('6) Delete Student Record')
		print('7) Save Records')
		print('ESC) Exit Program')
		choice = input('Choose an option: ').strip()

		if choice == '\x1b' or choice.upper() == 'ESC':
			print_section_heading('Exit')
			confirm_prompt = input('Do you want to save? (Y/N): ').strip().upper()
			if confirm_prompt == 'Y':
				save_records(DATA_FILE, students)
			print_closing_banner()
			print('='*50)
			break

		if choice == '1':
			print_section_heading('Add New Student')
			add_student(students)
			print('='*50)
			continue

		if choice == '2':
			print_section_heading('Display All Students')
			display_students(students)
			print('='*50)
			continue

		if choice == '3':
			print_section_heading('Modify Student Score')
			modify_student_score(students)
			print('='*50)
			continue

		if choice == '4':
			print_section_heading('Class Statistics')
			class_stats(students)
			print('='*50)
			continue

		if choice == '5':
			print_section_heading('Search Students')
			while True:
				term = input('Enter name to search (case-insensitive) or ESC to exit: ')
				if term == '\x1b' or term.upper() == 'ESC' or not term.strip():
					print('Search cancelled.')
					break
				if search_student(students, term):
					break
			print('='*50)
			continue

		if choice == '6':
			print_section_heading('Delete Student Record')
			delete_student_record(students)
			print('='*50)
			continue

		if choice == '7':
			print_section_heading('Save Records')
			save_records(DATA_FILE, students)
			print('='*50)
			continue

		print('Invalid choice. Please select 1-6 or press ESC to exit.')
		print('='*50)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('\nInterrupted. Exiting.')
		sys.exit(0)


