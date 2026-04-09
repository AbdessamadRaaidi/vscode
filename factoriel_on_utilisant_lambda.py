(lambda f: (lambda n: print(f"Le factoriel de {n} est {f(f, n)}"))
 (int(input("Entrez un nombre : "))))
(lambda self, n: 1 if n == 0 else n * self(self, n - 1))