from threading import Thread, Semaphore
import random, sys, time


class BarTable:
    def __init__(self):
        self.customers = 0
        self.leavers = 0

        self.status_changing = Semaphore(1)
        self.allowed_leaving = Semaphore(0)


class Student:
    def __init__(self, identifier):
        self.identifier = identifier


    def drink(self, table):
        print(f'O aluno {self.identifier} chegou e pediu uma cerveja...')
        time.sleep(random.random())

        table.status_changing.acquire()
        table.customers += 1
        if (table.customers == 2) and (table.leavers == 1):
            table.allowed_leaving.release()
            table.leavers -= 1
        table.status_changing.release()

        print(f'O aluno {self.identifier} começou a beber!')
        time.sleep(0.5)

        table.status_changing.acquire()
        print(f'O aluno {self.identifier} está esperando para ir embora...')
        table.customers -= 1
        table.leavers += 1


    def leave(self, table):
        if (table.customers == 1) and (table.leavers == 1):
            table.status_changing.release()
            table.allowed_leaving.acquire()

        elif (table.customers == 0) and (table.leavers == 2):
            table.allowed_leaving.release()
            table.leavers -= 2
            table.status_changing.release()

        else:
            table.leavers -= 1
            table.status_changing.release()

        print(f'O aluno {self.identifier} foi embora.')


def run_student(student, bar_table):
    student.drink(bar_table)
    student.leave(bar_table)


def main(n_students):
    bar_table = BarTable()
    students = [Student(i + 1) for i in range(n_students)]

    student_threads = [
        Thread(target=run_student, args=[student, bar_table])
        for student in students
    ]

    [student_thread.start() for student_thread in student_threads]


if __name__ == '__main__':
    has_arguments = (len(sys.argv) == 2)

    n_students = int(sys.argv[1]) if has_arguments else 7

    main(n_students)
