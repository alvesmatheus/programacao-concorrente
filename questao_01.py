from threading import Thread, Semaphore
import os, random, time

CAR_CAPACITY = 4
N_PASSENGERS = 12


class Car:
    def __init__(self, capacity):
        self.seats = capacity
        self.passengers = 0

        self.loading = Semaphore(0)
        self.unloading = Semaphore(0)
        self.loaded = Semaphore(0)
        self.unloaded = Semaphore(0)


    def is_full(self):
        return (self.passengers == self.seats)


    def is_empty(self):
        return (self.passengers == 0)


    def load(self):
        print('\nO carro está aguardando novos passageiros...\n')
        time.sleep(1)
        self.loading.release()


    def run(self):
        print('\nO carro está em movimento...')
        time.sleep(1)
        self.unload()


    def unload(self):
        print('O carro está desembarcando passageiros...\n')
        time.sleep(1)
        self.unloading.release()


class Passenger:
    def __init__(self, identifier):
        self.identifier = identifier
        self.onboard = False


    def board(self, car):
        print(f'O passageiro {self.identifier} embarcou!')
        self.onboard = True

        car.loading.acquire()
        car.passengers += 1
        if car.is_full():
            car.loaded.release()
        car.loading.release()


    def unboard(self, car):
        print(f'O passageiro {self.identifier} desembarcou!')
        self.onboard = False

        car.unloading.acquire()
        car.passengers -= 1
        if car.is_empty():
            car.unloaded.release()
        car.unloading.release()


def run_car(car, capacity, n_passengers, board_queue, unboard_queue):
    for _ in range(n_passengers // capacity):
        car.load()
        [board_queue.release() for _ in range(capacity)]
        car.loaded.acquire()

        car.run()
        [unboard_queue.release() for _ in range(capacity)]
        car.unloaded.acquire()


def run_passenger(passenger, car, board_queue, unboard_queue):
    time.sleep(random.random())
    board_queue.acquire()
    passenger.board(car)

    time.sleep(random.random())
    unboard_queue.acquire()
    passenger.unboard(car)


def main():
    board_queue = Semaphore(0)
    unboard_queue = Semaphore(0)
    kwargs = {'board_queue': board_queue, 'unboard_queue': unboard_queue}

    car = Car(CAR_CAPACITY)
    passengers = [Passenger(i + 1) for i in range(N_PASSENGERS)]

    car_thread = Thread(target=run_car,
                        args=[car, CAR_CAPACITY, N_PASSENGERS],
                        kwargs=kwargs)

    passenger_threads = [
        Thread(target=run_passenger, args=[passenger, car], kwargs=kwargs)
        for passenger in passengers
    ]

    car_thread.start()
    [passenger_thread.start() for passenger_thread in passenger_threads]


if __name__ == '__main__':
    main()
