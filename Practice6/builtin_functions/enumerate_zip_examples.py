n = int(input())
names = list(input().split())
scores = list(map(int, input().split()))
for name, score in zip(names, scores):
    print(name, score)

A = [1, 2, 3, 4, 5]
B = [6, 7, 8, 9, 10]
dot = sum(a * b for a, b in zip(A, B))
print(dot)

for index, name in enumerate(names, start = 1):
    print(index, name)