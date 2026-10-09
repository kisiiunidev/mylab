A = set((2, 3, 4, 5))
B = set((4, 5, 6, 7))

# | UNION
print(A | B)

# & INRESECTION
print(A & B)

# - Difference -> 
print(A - B)

# ^ SYMETRIC DIFFERENCE -> removes common in A and B
print(A ^ B)

X = {1, 2}
Y = {1, 2, 3, 4}

print(X.issubset(Y))
print(Y.issuperset(X))
print(A.isdisjoint({5, 6}))

