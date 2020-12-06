from threading import Thread, Semaphore
import random
import sys
import time


class Car:
    def __init__(self, capacity):
        self.seats = capacity  # Capacidade máxima do carro
        self.passengers = 0  # Passageiros dentro do carro atualmente

        self.loading = Semaphore(0)  # Os passageiros podem embarcar?
        self.unloading = Semaphore(0)  # Os passageiros podem desembarcar?
        self.loaded = Semaphore(0)  # Todos os passageiros embarcaram?
        self.unloaded = Semaphore(0)  # Todos os passageiros desembarcaram?

    def is_full(self):
        return (self.passengers == self.seats)

    def is_empty(self):
        return (self.passengers == 0)

    def load(self):
        print('\nO carro está aguardando novos passageiros...\n')
        self.loading.release()  # Um passageiro pode embarcar agora!

    def run(self):
        print('\nO carro está em movimento...')
        self.unload()

    def unload(self):
        print('O carro está desembarcando seus passageiros...\n')
        self.unloading.release()  # Um passageiro pode desembarcar agora!


class Passenger:
    def __init__(self, identifier):
        self.identifier = identifier  # Identificador único do passageiro
        self.onboard = False  # Indica se o passageiro está dentro do carro

    def board(self, car):
        print(f'O passageiro {self.identifier} embarcou!')
        self.onboard = True

        # Impede que outros passageiros embarquem simultaneamente, incrementa o
        # número de passageiros e, só então, permite que outros passageiros
        # embarquem. Antes disso, se a capacidade do carro for atingida, indica
        # ao carro que todos os passageiros já embarcaram.
        time.sleep(random.random())  # Espera randômica para embarcar
        car.loading.acquire()
        car.passengers += 1
        if car.is_full():
            car.loaded.release()
        car.loading.release()

    def unboard(self, car):
        print(f'O passageiro {self.identifier} desembarcou!')
        self.onboard = False

        # Impede que outros passageiros desembarquem simultanemante, decrementa
        # o número de passageiros e, só então, permite que outros passageiros
        # desembarquem. Antes disso, se não houver mais passageiros no carro,
        # indica ao carro que todos os passageiros já desembarcaram.
        time.sleep(random.random())  # Espera randômica para desembarcar
        car.unloading.acquire()
        car.passengers -= 1
        if car.is_empty():
            car.unloaded.release()
        car.unloading.release()


def run_car(car, capacity, n_passengers, board_queue, unboard_queue):
    # Inicialmente, o carro está aguardando novos passageiros. Ele permanecerá
    # assim até que sua capacidade seja atingida, o que ocorre quando o último
    # passageiro possível entra no carro e indica isso através do `loaded`.
    # Assim, carro entrará em movimento e passará a aguardar o desembarque dos
    # passageiros. O último passageiro a desembarcar indica ao carro que ele
    # está vazio através do `unloaded`. O processo se repetirá de acordo com o
    # o número de viagens que o carro poderá realizar com o os passageiros
    # existentes.
    for _ in range(n_passengers // capacity):
        car.load()
        [board_queue.release() for _ in range(capacity)]
        car.loaded.acquire()

        car.run()
        [unboard_queue.release() for _ in range(capacity)]
        car.unloaded.acquire()


def run_passenger(passenger, car, board_queue, unboard_queue):
    # Um passageiro aguardará na fila até que possa embarcar no carro, o que
    # só ocorrerá se o carro estiver aguardando novos passageiros e nenhum
    # outro passageiro estiver embarcando simultaneamente. De forma análoga,
    # quando o carro permitir o desembarque dos passageiros que embarcaram
    # o passageiro não desembarcará a menos que nenhum outro passageiro esteja
    # desembarcando ao mesmo tempo.
    board_queue.acquire()
    passenger.board(car)

    unboard_queue.acquire()
    passenger.unboard(car)


def main(n_passengers, car_capacity):
    board_queue = Semaphore(0)  # Quantos passageiros irão embarcar?
    unboard_queue = Semaphore(0)  # Quantos passageiros irão desembarcar?
    kwargs = {'board_queue': board_queue, 'unboard_queue': unboard_queue}

    car = Car(car_capacity)
    passengers = [Passenger(i + 1) for i in range(n_passengers)]
    random.shuffle(passengers)  # Randomiza a ordem de início das threads

    car_thread = Thread(target=run_car,
                        args=[car, car_capacity, n_passengers],
                        kwargs=kwargs)

    passenger_threads = [
        Thread(target=run_passenger, args=[passenger, car], kwargs=kwargs)
        for passenger in passengers
    ]

    car_thread.start()
    [passenger_thread.start() for passenger_thread in passenger_threads]


if __name__ == '__main__':
    has_arguments = (len(sys.argv) == 3)

    n_passengers = int(sys.argv[1]) if has_arguments else 8
    car_capacity = int(sys.argv[2]) if has_arguments else 4

    main(n_passengers, car_capacity)
