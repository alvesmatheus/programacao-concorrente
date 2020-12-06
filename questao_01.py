from threading import Thread, Semaphore
import random, sys, time


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


def main(n_passengers, car_capacity):
    board_queue = Semaphore(0)
    unboard_queue = Semaphore(0)
    kwargs = {'board_queue': board_queue, 'unboard_queue': unboard_queue}

    car = Car(car_capacity)
    passengers = [Passenger(i + 1) for i in range(n_passengers)]

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
