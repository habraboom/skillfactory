import random
from random import randint, choice



class ShipsCrossingError(Exception):
    def __str__(self):
        return "Координаты кораблей пересекаются!"


class ShipCoordinatesError(Exception):
    def __str__(self):
        return "Координаты корабля должны быть в виде 'А1Б1В1' или 'А1'"


class ShipsCountError(Exception):
    def __str__(self):
        return "Кораблей должно быть 7 штук (1 х 3 палубный, 2 х 2 палубных, 4 х 1 палубных)"


class Point:

    def __init__(self, name: str, hide_points: bool):
        self._name = name.upper()
        self._ship = None  # для удобства точка будет знать, какому кораблю принадлежит
        self._near_ship = False  # точка возле корабля, обычная, но ставить корабль туда нельзя
        self._coordinates = self.get_coordinates(name)
        self._injured = False  # ранен
        self._missed = False  # промах
        self._hide_points = hide_points  # скрывать корабли компьютера

    def __str__(self):
        return self._name

    def do_step(self):
        if self.ship is None:
            self.missed = True
            return False
        else:
            self.injured = True
            self.ship.check_killed()
            return True

    @property
    def hide_points(self):
        return self._hide_points

    @property
    def missed(self):
        return self._missed

    @missed.setter
    def missed(self, value):
        self._missed = value

    @property
    def injured(self):
        return self._injured

    @injured.setter
    def injured(self, value):
        self._injured = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = value

    @property
    def ship(self):
        return self._ship

    @ship.setter
    def ship(self, ship):
        self._ship = ship

    @property
    def value(self):
        if self.injured:
            return "X"
        elif self.missed:
            return "T"
        elif not self.hide_points and self.ship is not None:
            return "■"
        else:
            return "O"

    @property
    def near_ship(self):
        return self._near_ship

    @near_ship.setter
    def near_ship(self, value):
        self._near_ship = value

    @staticmethod
    def points_dct() -> dict:
        h, v = "АБВГДЕ", "123456"
        # {'А1': (0, 0), 'Б1': (0, 1), 'В1': (0, 2) ... 'Д6': (5, 4), 'Е6': (5, 5)}
        return {h[i] + v[j]: (j, i) for j in range(len(v)) for i in range(len(h))}

    @staticmethod
    def reverse_points_dct() -> dict:
        return {value: key for key, value in Point.points_dct().items()}

    @staticmethod
    def get_coordinates(name: str) -> tuple:
        coordinates = Point.points_dct()[name.upper().strip()]
        if coordinates is None:
            raise ShipCoordinatesError
        return coordinates


class Ship:
    def __init__(self, points, hide_points):
        self._points = self.init_ship_dots(points, hide_points)  # точки корабля
        for point in self._points:
            point.ship = self

        self._points_around = self.init_ship_dots_around(self._points, hide_points)  # точки вокруг корабля (буфер)
        for point in self._points_around:
            point.near_ship = True

        self._killed = False  # Признак, что корабль убит
        self._hide_points = hide_points  # Триггер - показывать или нет корабль.

    @property
    def points(self):
        return self._points

    @property
    def hide_points(self):
        return self._hide_points

    @property
    def points_around(self):
        return self._points_around

    @property
    def killed(self):
        return self._killed

    def __str__(self):  # представление корабля в формате А1Б1
        return "".join([str(i) for i in self._points])

    @staticmethod
    def init_ship_dots(points, hide_points):
        dct = Point.points_dct()
        ship_coordinates = []
        ship_points = []
        for i in range(0, len(points), 2):
            dot = points[i:i + 2].upper()
            ship_points.append(dot)
            if dot not in dct:
                raise ShipCoordinatesError
            ship_coordinates.append(dct[dot])

        #  Проверим, что координаты - в ряд или в столбец и без дырок (т.е. не указали корабль как А3А5 или А1Б2).
        if len(ship_coordinates) > 1:
            x_coordinates = [coord[0] for coord in ship_coordinates]
            y_coordinates = [coord[1] for coord in ship_coordinates]
            if min(x_coordinates) == max(x_coordinates):
                for i in range(len(ship_coordinates) - 1):
                    if y_coordinates[i] + 1 != y_coordinates[i + 1]:
                        raise ShipCoordinatesError
            elif min(y_coordinates) == max(y_coordinates):
                for i in range(len(ship_coordinates) - 1):
                    if x_coordinates[i] + 1 != x_coordinates[i + 1]:
                        raise ShipCoordinatesError
            else:
                raise ShipCoordinatesError

        return [Point(dot, hide_points) for dot in ship_points]

    @staticmethod
    def init_ship_dots_around(points, hidden):
        points_around_ship = []
        points_ship = [p.coordinates for p in points]
        # Для каждой точки корабля отмечаем все смежные (т.е. все точки вокруг) и тоже заполняем, чтобы потом
        # следующий корабль не попадал на эти точки.
        for point in points:
            x, y = point.coordinates  # сама точка попадет в проверку как часть множества
            for i in [-1, 0, 1]:  # смещение по x
                curr_x = x + i
                for j in [-1, 0, 1]:  # смещение по y
                    curr_y = y + j
                    # смотрим, чтобы точка не уехала за границы поля
                    if 0 <= curr_x <= 5 and 0 <= curr_y <= 5:
                        curr_point = (curr_x, curr_y)
                        if curr_point not in (points_ship + points_around_ship):
                            points_around_ship.append(curr_point)
        res = []
        dct = Point.points_dct()
        for curr_point in points_around_ship:
            for key, value in dct.items():
                if curr_point == value:
                    res.append(Point(key, hidden))

        return res

    def check_killed(self):
        for point in self._points:
            if not point.injured:
                return
        print(f"Корабль {self} убит!")
        self._killed = True


class Board:
    def __init__(self, ships, hide_points, raise_error=True):
        Board.check_ships(ships)

        # Инициализация доски
        self._points = {key: Point(key, hide_points) for key in Point.points_dct().keys()}
        self._ships = ships
        self._hide_points = hide_points

        # Каждый корабль расставляем на доске
        for ship in ships:
            for point in ship.points:
                curr_point = self._points[point.name]
                if curr_point.ship is not None or curr_point.near_ship:
                    if raise_error:
                        raise ShipsCrossingError
                    else:
                        self._error = True
                        break
                self._points[point.name] = point

            for point_near in ship.points_around:
                curr_point = self._points[point_near.name]
                if curr_point.ship is None:
                    self._points[point_near.name] = point_near

    def __str__(self):
        rows = ["      (поле компьютера)"] if self._hide_points else ["      (поле человека)"]
        rows.append("  | А | Б | В | Г | Д | Е |")
        cnt = 0
        for i in "123456":
            cnt += 1
            row = str(cnt)
            for j in "АБВГДЕ":
                row += " | " + self._points[j + i].value
            row += " | "
            rows.append(row)
        return "\n".join(rows)

    @staticmethod
    def check_ships(ships):
        #  кораблей должно быть 7
        if len(ships) != 7:
            raise ShipsCountError

        # длины кораблей должны быть [3, 2, 2, 1, 1, 1, 1]
        standard = [3, 2, 2, 1, 1, 1, 1]
        for ship in ships:
            curr_len = len(ship.points)
            if curr_len in standard:
                standard.remove(curr_len)

        if len(standard) > 0:
            raise ShipsCountError

    @property
    def error(self):
        return hasattr(self, "_error")

    @property
    def points(self):
        return self._points

    @property
    def ships(self):
        return self._ships

    def has_winner(self):
        for ship in self.ships:
            if not ship.killed:
                return False
        return True

    def human_step(self):
        print(self)
        coordinates = input("Введите координаты: ").strip().upper()
        point = self.points.get(coordinates, None)
        if point is None:
            print("Вы передали кривое значение ячейки, попробуйте еще раз")
            self.human_step()
        elif point.injured or point.missed:
            print("Вы сюда уже стреляли! Попробуйте еще раз")
            self.human_step()
        else:
            if point.do_step():
                if self.has_winner():
                    return
                else:
                    print("Вы попали, делайте еще выстрел!")
                    self.human_step()
            else:
                print("Вы промазали, теперь ходит компьютер")
                print(self)

    def computer_step(self):
        while True:
            # coordinates = Point.reverse_points_dct()[(randint(0, 5), randint(0, 5))]
            # point = self.points[coordinates.strip().upper()]
            point = random.choice(list(self.points.values()))
            if not point.injured and not point.missed:
                break

        print("Компьютер стреляет в", point.coordinates)
        if point.do_step():
            if self.has_winner():
                return
            else:
                print("Компьютер попал, снова стреляет!")
                print(self)
                self.computer_step()
        else:
            print("Компьютер промазал, переход хода!")
            print(self)


def get_computer_board(cheater=False):
    #  Генерируем произвольные наборы, пока случайно не получим корректную расстановку кораблей
    cnt = 0
    while True:
        cnt += 1
        ships = generate_random_ships()
        if ships is None:
            continue

        board = Board(ships, True, False)
        if not board.error:
            if cheater:  # чтобы подсматривать за компьютером
                print("Расстановка компьютера:", board.ships)
                for ship in board.ships:
                    print(ship, end=", ")
            print("Компьютер расставил корабли за", str(cnt), "попыток")
            return board


def generate_random_ships():
    ships = []
    ln = [3, 2, 2, 1, 1, 1, 1]
    for i in range(len(ln)):
        if i == 0:
            x, y = randint(0, 1), randint(0, 1)
        elif i == 1:
            x, y = randint(0, 2), randint(4, 5)
        elif i == 2:
            x, y = randint(4, 5), randint(0, 2)
        else:
            x, y = randint(0, 5), randint(0, 5)

        # Генерируем произвольную точку и от нее вправо или вниз набираем еще точки корабля
        curr_ship = Point.reverse_points_dct()[(x, y)]
        direction = randint(0, 1)
        for n in range(1, ln[i]):
            curr_key = (x + n, y) if direction == 0 else (x, y + n)
            if curr_key in Point.reverse_points_dct().keys():
                curr_ship += Point.reverse_points_dct()[curr_key]
            else:
                return None  # если сгенерировали диапазон, выходящий за поле

        ships.append(Ship(curr_ship, True))

    return ships


def main():
    #   | А | Б | В | Г | Д | Е |
    # 1 | ■ | ■ | ■ | О | ■ | О |
    # 2 | О | О | О | О | ■ | О |
    # 3 | О | О | О | О | О | О |
    # 4 | ■ | ■ | О | ■ | О | ■ |
    # 5 | О | О | О | О | О | О |
    # 6 | ■ | О | О | О | ■ | О |
    imp = input("""Введите координаты всех кораблей (1 x 3 клетки, 2 x 2 клетки, 4 x 1 клетку)
    Ожидаемый формат: А1Б1В1 Д1Д2 А4Б4 Г4 Е4 А6 Д6: """)
    # imp = "А1Б1В1 Д1Д2 А4Б4 Г4 Е4 А6 Д6"
    ships = [Ship(coordinate.upper(), False) for coordinate in imp.strip().split()]
    human_board = Board(ships, False)
    print(human_board)
    print("Тут может задуматься на какое-то время, т.к. компьютер долго расставляет корабли :)")
    computer_board = get_computer_board()
    humans_turn = True
    while True:
        if humans_turn:
            computer_board.human_step()
            if computer_board.has_winner():
                print("Победил человек!")
                break
        else:
            human_board.computer_step()
            if human_board.has_winner():
                print("Победил компьютер!")
                break
        humans_turn = not humans_turn


if __name__ == '__main__':
    main()
