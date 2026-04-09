def add(x, y):
    return x + y
def subtract(x, y):
    return x - y
def multiply(x, y):
    return x * y
def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y
print("Select operation:")
print("1.Add")
print("2.Subtract")
print("3.Multiply")
print("4.Divide")
c = input("Entrer choix(1/2/3/4): ")
n= float(input("Entrer nombre 1: "))
m = float(input("Entrer nombre 2: "))
if c == '1':
    print(f"{n} + {m} = {add(n, m)}")
elif c == '2':
    print(f"{n} - {m} = {subtract(n, m)}")
elif c == '3':
    print(f"{n} * {m} = {multiply(n, m)}")
elif c == '4':
    print(f"{n} / {m} = {divide(n, m)}")
else:    print("Invalid input")