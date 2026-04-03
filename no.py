print("Hello, World!")
if 5 > 3:
    print("5 is greater than 3")
for i in range(5):
    print(i)
def greet(name):
    return f"Hello, {name}!"
print(greet("Alice"))
class Person:
    def __init__(self, name):
        self.name = name
    def say_hello(self):
        return f"{self.name} says hello!"
person = Person("Bob")
print(person.say_hello())
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Error: Division by zero is not allowed.")
with open("example.txt", "w") as file:    file.write("This is an example file.")
import math

import pygame
print(math.sqrt(16))
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
print(factorial(5))
import random
print(random.randint(1, 10))
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    else:
        fib_sequence = [0, 1]
        for i in range(2, n):
            next_fib = fib_sequence[i - 1] + fib_sequence[i - 2]
            fib_sequence.append(next_fib)
        return fib_sequence
print(fibonacci(10))
def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True
print(is_prime(17))