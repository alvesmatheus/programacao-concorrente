from threading import Thread, Lock, Semaphore
import random
import sys
import time


class Barrier:
    # Implementação de uma barreira reusável para que seja utilizada na questão
    # sem infringir as restrições da avaliação.
    def __init__(self, capacity):
        self.capacity = capacity
        self.waiting_threads = 0

        self.mutex = Lock()
        self.in_gate = Semaphore(0)
        self.out_gate = Semaphore(1)

    def is_full(self):
        return (self.waiting_threads == self.capacity)

    def is_empty(self):
        return (self.waiting_threads == 0)

    def acquire(self):
        self.mutex.acquire()
        self.waiting_threads += 1
        if self.is_full():
            self.out_gate.acquire()
            self.in_gate.release()
        self.mutex.release()

        self.in_gate.acquire()
        self.in_gate.release()

    def release(self):
        self.mutex.acquire()
        self.waiting_threads -= 1
        if self.is_empty():
            self.in_gate.acquire()
            self.out_gate.release()
        self.mutex.release()

        self.out_gate.acquire()
        self.out_gate.release()


class Boat:
    def __init__(self):
        self.ufcg_students = 0  # Número de estudantes da UFCG no barco
        self.uepb_students = 0  # Número de estudantes da UEPB no barco

        self.mutex = Lock()  # Mutex para garantir consistência nos atributos
        # Barreira para garantir que a viagem só seja iniciada com 4 estudantes
        self.barrier = Barrier(4)


class Student:
    def __init__(self, identifier, university):
        self.identifier = identifier  # Identificador único do estudante
        self.university = university  # Universidade de origem do estudante
        self.rower = False  # Identificador do aluno responsável por remar

    def board(self, boat, ufcg_queue, uepb_queue):
        # A operação de embarcar um estudante varia conforme a universidade de
        # origem do estudante. Para um estudante qualquer, é necessário começar
        # bloqueando outros estudantes de alterarem os atributos do barco e,
        # em seguida, incrementar o número de estudantes da sua universidade
        # de origem. Se esse novo estudante fizer com que o barco tenha 4
        # estudantes de sua universidade ou 2 estudantes de cada universidade,
        # ele será o remador e o barco seguirá viagem.
        #
        # Ao fazer isso, será decrementado do barco o número de estudantes de
        # cada universidade que estava nessa viagem. Caso nenhuma das condições
        # seja satisfeita, o estudante apenas permitirá que outros estudantes
        # voltem a poder alterar os atributos do barco. Visto que o remador é
        # sempre responsável por iniciar a viagem, antes e depois que ele reme
        # é necessário realizar o acquire e release (respectivamente) da
        # barreira do barco.
        if (self.university == 'UFCG'):
            self.board_ufcg_student(boat, ufcg_queue, uepb_queue)
        elif (self.university == 'UEPB'):
            self.board_uepb_student(boat, ufcg_queue, uepb_queue)

        boat.barrier.acquire()
        if self.rower:
            self.row(boat)
        boat.barrier.release()

    def board_ufcg_student(self, boat, ufcg_queue, uepb_queue):
        boat.mutex.acquire()
        boat.ufcg_students += 1

        if (boat.ufcg_students == 4):
            [ufcg_queue.release() for _ in range(4)]
            boat.ufcg_students = 0
            self.rower = True
        elif (boat.ufcg_students == 2) and (boat.uepb_students >= 2):
            [ufcg_queue.release() for _ in range(2)]
            [uepb_queue.release() for _ in range(2)]
            boat.ufcg_students = 0
            boat.uepb_students -= 2
            self.rower = True
        else:
            boat.mutex.release()

        ufcg_queue.acquire()
        print((f'O estudante {self.identifier} da {self.university} ' +
               f'embarcou...'))

    def board_uepb_student(self, boat, ufcg_queue, uepb_queue):
        boat.mutex.acquire()
        boat.uepb_students += 1

        if (boat.uepb_students == 4):
            [uepb_queue.release() for _ in range(4)]
            boat.uepb_students = 0
            self.rower = True
        elif (boat.uepb_students == 2) and (boat.ufcg_students >= 2):
            [ufcg_queue.release() for _ in range(2)]
            [uepb_queue.release() for _ in range(2)]
            boat.uepb_students = 0
            boat.ufcg_students -= 2
            self.rower = True
        else:
            boat.mutex.release()

        uepb_queue.acquire()
        print((f'O estudante {self.identifier} da {self.university} ' +
               f'embarcou...'))

    def row(self, boat):
        print((f'O estudante {self.identifier}, da {self.university}, remou ' +
               'e levou todos os passageiros até o outro lado do açude!\n'))
        boat.mutex.release()


def main(ufcg_students, uepb_students):
    ufcg_queue = Semaphore(0)  # Quantos estudantes da UFCG desejam embarcar?
    uepb_queue = Semaphore(0)  # Quantos estudantes da UEPB desejam embarcar?

    boat = Boat()
    students = []
    students.extend([Student(i + 1, 'UFCG') for i in range(ufcg_students)])
    students.extend([Student(i + 1, 'UEPB') for i in range(uepb_students)])
    random.shuffle(students)  # Randomiza a ordem de início das threads

    student_threads = [
        Thread(target=student.board, args=[boat, ufcg_queue, uepb_queue])
        for student in students
    ]

    [student_thread.start() for student_thread in student_threads]


if __name__ == '__main__':
    has_arguments = (len(sys.argv) == 3)

    ufcg_students = int(sys.argv[1]) if has_arguments else 6
    uepb_students = int(sys.argv[2]) if has_arguments else 6

    main(ufcg_students, uepb_students)
