from ortools.linear_solver import pywraplp

arq = open("input.txt")

n = int(arq.readline())
m = int(arq.readline())
B = float(arq.readline())
T = float(arq.readline())
F = float(arq.readline())

# le as materias primas do arquivo (a)       a[mat][prod]
a = []
for j in range(m):
    line = arq.readline()
    values = line.split()

    aux = []

    for i in range(n):
        aux.append(int(values[i]))

    a.append(aux)

# le tempo de producao de cada produto (b)
b = []
line = arq.readline()
values = line.split()

for i in range(n):
    b.append(float(values[i]))

# le as demandas minimas de cada produto (d_min)
d_min = []
line = arq.readline()
values = line.split()

for i in range(n):
    d_min.append(int(values[i]))

# le as demandas maximas de cada produto (d_max)
d_max = []
line = arq.readline()
values = line.split()

for i in range(n):
    d_max.append(int(values[i]))

# le o preco de venda de cada produto (R)
R = []
line = arq.readline()
values = line.split()

for i in range(n):
    R.append(float(values[i]))

# le a quantidade do materia-prima em um lote (L)
L = []
line = arq.readline()
values = line.split()

for j in range(m):
    L.append(int(values[j]))

# le o custo de cada lote de materia-prima (C)
C = []
line = arq.readline()
values = line.split()

for j in range(m):
    C.append(float(values[j]))

#------------- Inicia o processo do solver -------------#

solve = pywraplp.Solver.CreateSolver('SCIP')
infinity = solve.infinity()


#----------------- Variaveis do solver -----------------#
produtos = []
lotes = []
prod_flag = []

for i in range(n):
    produtos.append(solve.IntVar(0.0, infinity, f'produtos[{i}]'))

for j in range(m):
    lotes.append(solve.IntVar(0.0, infinity, f'lotes[{j}]'))

for i in range(n):
    prod_flag.append(solve.IntVar(0.0, 1.0, f'prod_flag[{i}]'))

#--------------- Adicionando restricoes ----------------#

solve.Add(solve.Sum([produtos[i] * b[i] for i in range(n)]) +
          (solve.Sum([prod_flag[i] for i in range(n)]) - 1) * T <= B)

for i in range(n):
    solve.Add(produtos[i] >= d_min[i] * prod_flag[i])

for i in range(n):
    solve.Add(produtos[i] <= d_max[i] * prod_flag[i])

for j in range(m):
    solve.Add(solve.Sum([produtos[i] * a[j][i]
              for i in range(n)]) <= lotes[j] * L[j])

for i in range(n):
    solve.Add(bool(prod_flag[i]) == bool(produtos[i]))


#-------------- Resolvendo o problema ------------------#


solve.Maximize(solve.Sum([produtos[i] * R[i] for i in range(n)]) -
               solve.Sum([lotes[j] * C[j] for j in range(m)]) - F)


#-------------- Saida do programa ----------------------#

if solve.Solve() == pywraplp.Solver.OPTIMAL:
    print("-------------------------------------------------------------------------------------------------")

    prod_total = 0
    horas_totais = 0
    for i in range(n):
        if prod_flag[i].solution_value():
            prod_total = prod_total + \
                float(produtos[i].solution_value() * R[i])
            horas_totais = horas_totais + produtos[i].solution_value()*b[i]
            print(
                f'Foram produzidas {int(produtos[i].solution_value())} unidades de p{i+1}, consumindo {produtos[i].solution_value()*b[i]} horas, e gerando um total de R$ {float(produtos[i].solution_value()* R[i])}')

    print("-------------------------------------------------------------------------------------------------")

    lote_total = 0
    for j in range(m):
        if lotes[j].solution_value():
            lote_total = lote_total + float(lotes[j].solution_value()*C[j])
            print(
                f'Foram comprados {lotes[j].solution_value()} lotes de m{j+1}, gastando um total de R$ {float(lotes[j].solution_value()*C[j])}')

    print("-------------------------------------------------------------------------------------------------")

    print(f'Foram gastas {horas_totais} horas para a produção dos produtos')

    horas_troca = -20
    for i in range(n):
        if prod_flag[i].solution_value():
            horas_troca = horas_troca + 20

    print(
        f'Foram gastas {horas_troca} horas na troca de produtos na linha de produção')

    print(
        f'Foram gastas um total de {horas_totais + horas_troca} horas em toda linha de produção')

    print("-------------------------------------------------------------------------------------------------")

    print(f'Renda total dos produtos = R$ {prod_total}')

    print(f'Custo de materia-prima = R$ {lote_total}')

    print(f'Gasto mensal fixo = R$ {F}\n')

    print(f'Lucro = R$ {round(float(solve.Objective().Value()), 2)}')

    print("-------------------------------------------------------------------------------------------------")
