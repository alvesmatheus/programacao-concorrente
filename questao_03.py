from threading import Thread, Semaphore
import random
import sys
import time


class BarTable:
    def __init__(self):
        self.customers = 0  # Número de alunos que estão bebendo
        self.leavers = 0  # Número de alunos que estão remedidados

        self.status_changing = Semaphore(1)  # Alunos podem mudar de estado?
        self.allowed_leaving = Semaphore(0)  # Alunos podem ir embora?


class Student:
    def __init__(self, identifier):
        self.identifier = identifier  # Identificador único do aluno

    def drink(self, table):
        print(f'O aluno {self.identifier} chegou e pediu uma cerveja...')
        time.sleep(random.random())  # Espera randômica para começar a beber

        # Quando um aluno chega ao bar, ele pede sua bebida. Se já havia um
        # aluno A remediado que não podia ir embora porque um aluno B ainda
        # estava bebendo, o aluno A irá embora. A seguir, o aluno que chegou
        # começa e beber e, quando termina, muda de estado para remediado se,
        # e somente se, nenhum outro aluno estiver mudando de estado ao mesmo
        # tempo.
        table.status_changing.acquire()
        table.customers += 1
        if (table.customers == 2) and (table.leavers == 1):
            table.allowed_leaving.release()
            table.leavers -= 1
        table.status_changing.release()

        print(f'O aluno {self.identifier} começou a beber!')
        time.sleep(random.random())  # O aluno bebe durante um tempo randômico

        table.status_changing.acquire()
        print(f'O aluno {self.identifier} está esperando para ir embora...')
        table.customers -= 1
        table.leavers += 1

    def leave(self, table):
        # Quando um aluno deseja ir embora, primeiro ele deverá checar se na
        # mesa resta apenas um aluno além dele. Se isso ocorrer e o aluno ainda
        # está bebendo, ele ficara aguardando a permissão para ir embora. Já
        # se o outro aluno á estava aguardando, ambos irão embora juntos. Por
        # fim, se há mais de um aluno na mesa quando o aluno decidiu ir embora,
        # ele não precisará se preocupar com eles e apenas irá embora.
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
    # O comportamento do aluno consiste apenas em ir até o bar, beber e ir
    # embora. As restrições impostas a esses comportamento estão descritas na
    # classe Student.
    student.drink(bar_table)
    student.leave(bar_table)


def main(n_students):
    bar_table = BarTable()
    students = [Student(i + 1) for i in range(n_students)]
    random.shuffle(students)  # Randomiza a ordem de início das threads

    student_threads = [
        Thread(target=run_student, args=[student, bar_table])
        for student in students
    ]

    [student_thread.start() for student_thread in student_threads]


if __name__ == '__main__':
    has_arguments = (len(sys.argv) == 2)

    n_students = int(sys.argv[1]) if has_arguments else 7

    main(n_students)
