class Averg:
    def get_average(self,*args):
        if not args:
            return 0
        return sum(args) / len(args)

numbers=[]
while True:
    number = input("Введите число(для завершения введите пустую строку):")
    if not number:
        break

    numbers.append(float(number))


average = Averg()

print("Среднее значение:", average.get_average(*numbers))



