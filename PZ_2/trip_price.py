class TripPrice:
    def __init__(self, first=0, second=0, third=0):
        self.__first = first
        self.__second = second
        self.__third = third

    @property
    def first(self):
        return self.__first

    @first.setter
    def first(self, value):
        if value <= 0:
            raise ValueError("Расстояние должно быть положительным")
        self.__first = value

    @property
    def second(self):
        return self.__second

    @second.setter
    def second(self, value):
        if value <= 0:
            raise ValueError("Расход топлива должен быть положительным")
        self.__second = value

    @property
    def third(self):
        return self.__third

    @third.setter
    def third(self, value):
        if value <= 0:
            raise ValueError("Цена должна быть положительной")
        self.__third = value

    def read(self):
        try:
            self.first = float(input("Введите растояние в км: "))
            self.second = float(input("Введите расход топлива на 100 км в литрах: "))
            self.third = float(input("Введите цену топлива за литр в рублях: "))
        except ValueError:
            print("Ошибка", ValueError)

    def display(self):
        print(f"Расстояние: {self.first} км")
        print(f"Расход: {self.second} литров на 100 км")
        print(f"Цена: {self.third} рублей")

    def calculate(self):
        liters = self.first * self.second / 100
        return liters * self.third

trip = TripPrice()
trip.read()
trip.display()
print("Стоимость поездки:", trip.calculate())