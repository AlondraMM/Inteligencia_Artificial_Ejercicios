# Reporte - Comparación de Greedy y A* en el mapa de Rumania

## Pareja elegida

- Origen: `Timisoara`
- Destino: `Bucharest`

La heuristica usada fue `straight-line distance to Bucharest (AIMA table)`.
Como el destino es `Bucharest`, se usa la tabla AIMA de distancia en linea
recta, que es admisible y consistente.

## Diagrama del subgrafo relevante

El número junto a cada ciudad es `h(n)` hacia `Bucharest`. Las aristas están en
kilómetros.

```text
Timisoara h=329 --118-- Arad h=366 --140-- Sibiu h=253 --99-- Fagaras h=176 --211-- Bucharest h=0
      |
     111
      |
 Lugoj h=244 --70-- Mehadia h=241 --75-- Drobeta h=242 --120-- Craiova h=160
                                                                            |
                                                                           138
                                                                            |
Rimnicu Vilcea h=193 --97-- Pitesti h=100 --101-- Bucharest h=0
        |
       80
        |
   Sibiu h=253

También existe: Rimnicu Vilcea h=193 --146-- Craiova h=160
```

## Tabla comparativa

| Algoritmo | Heuristica | Status | Path | Depth | Cost | Expanded | Generated |
|---|---|---|---|---:|---:|---:|---:|
| Greedy best-first | AIMA SLD to Bucharest | success | Timisoara -> Lugoj -> Mehadia -> Drobeta -> Craiova -> Pitesti -> Bucharest | 6 | 615 km | 6 | 15 |
| A* | AIMA SLD to Bucharest | success | Timisoara -> Arad -> Sibiu -> Rimnicu Vilcea -> Pitesti -> Bucharest | 5 | 536 km | 10 | 27 |
| UCS, reto opcional | sin heuristica | success | Timisoara -> Arad -> Sibiu -> Rimnicu Vilcea -> Pitesti -> Bucharest | 5 | 536 km | 12 | 31 |

## Tabla g / h / f

### Greedy

| Ciudad | g | h | f = g + h |
|---|---:|---:|---:|
| Timisoara | 0 | 329 | 329 |
| Lugoj | 111 | 244 | 355 |
| Mehadia | 181 | 241 | 422 |
| Drobeta | 256 | 242 | 498 |
| Craiova | 376 | 160 | 536 |
| Pitesti | 514 | 100 | 614 |
| Bucharest | 615 | 0 | 615 |

### A*

| Ciudad | g | h | f = g + h |
|---|---:|---:|---:|
| Timisoara | 0 | 329 | 329 |
| Arad | 118 | 366 | 484 |
| Sibiu | 258 | 253 | 511 |
| Rimnicu Vilcea | 338 | 193 | 531 |
| Pitesti | 435 | 100 | 535 |
| Bucharest | 536 | 0 | 536 |

## Análisis

A* sí encontró el camino de menos kilómetros. Para comprobarlo, se corrió la misma
pareja con UCS en el proyecto de busqueda no informada, y UCS devolvió el mismo
camino y el mismo costo que A*: `Timisoara -> Arad -> Sibiu -> Rimnicu Vilcea
-> Pitesti -> Bucharest`, con 536 km. Esto es lo esperado porque la heurística
de distancia en linea recta a Bucharest es admisible y consistente.

Greedy se desvió. Desde `Timisoara`, sus vecinos son `Arad` y `Lugoj`.
Comparando solo `h`, `Lugoj` parece mejor porque `h(Lugoj)=244`, mientras que
`h(Arad)=366`. Por eso Greedy toma `Lugoj`, aunque esa decisión lo lleva por
`Mehadia`, `Drobeta`, `Craiova` y `Pitesti`, acumulando 615 km. El problema es
que Greedy ignora `g(n)`, es decir, no considera cuánto costo lleva acumulado.
Una heurística admisible ayuda a estimar la cercanía al destino, pero no basta
para garantizar optimalidad si el algoritmo no suma el costo real ya pagado.

A* corrige ese problema usando `f(n) = g(n) + h(n)`. Un punto claro aparece
cerca de `Sibiu`: si solo se mira `h`, `Fagaras` parece mejor que
`Rimnicu Vilcea` porque `h(Fagaras)=176` y `h(Rimnicu Vilcea)=193`. Pero A*
considera también el costo acumulado: por `Fagaras`, `f=357+176=533`; por
`Rimnicu Vilcea`, `f=338+193=531`. Aunque `Rimnicu Vilcea` se ve un poco más
lejos en línea recta, su costo acumulado es menor, así que A* lo prefiere y
termina en la ruta optima.

En el camino final de A*, los valores de `f` tienden a no disminuir:
329, 484, 511, 531, 535, 536. Esto se relaciona con la consistencia de la
heuristica: al avanzar por una arista, el estimado restante no baja de forma
que contradiga el costo real del paso. Por eso A* puede expandir de forma
ordenada y garantizar el menor costo en esta versión de búsqueda en grafo.

## Reto opcional

### Greedy vs A*

La pareja `Timisoara -> Bucharest` cumple el reto opcional porque Greedy y A*
discrepan claramente:

| Algoritmo | Cost | Expanded | Generated | Observacion |
|---|---:|---:|---:|---|
| Greedy | 615 km | 6 | 15 | Trabajo menos, pero eligio una ruta mas cara. |
| A* | 536 km | 10 | 27 | Trabajo mas, pero encontro el costo optimo. |
| UCS | 536 km | 12 | 31 | Confirma el costo optimo de A*. |

En esta instancia, Greedy expandió menos nodos que A*, pero la ruta fue 79 km
mas cara. A* expandió más nodos porque compara alternativas mediante `g+h`,
pero esa exploración adicional evita el desvío caro.

### Misma pareja con UCS

UCS devolvió el mismo costo que A*:

```text
Timisoara -> Arad -> Sibiu -> Rimnicu Vilcea -> Pitesti -> Bucharest
Cost: 536 km
```

Esto confirma que A* encontró la ruta óptima en kilómetros. Greedy no coincide
con UCS porque no optimiza costo acumulado.

### Cambio de destino con el mismo origen

Cambiando solo el destino, manteniendo `Timisoara` como origen:

| Origen | Destino | Heuristica usada | Greedy | A* | Coinciden? |
|---|---|---|---:|---:|---|
| Timisoara | Bucharest | AIMA SLD to Bucharest | 615 km | 536 km | No |
| Timisoara | Eforie | Euclidean distance to Eforie | 884 km | 805 km | No |

Al cambiar el destino a `Eforie`, la etiqueta de la heurística cambia a
`Euclidean distance to Eforie (map coordinates)`, porque la tabla AIMA solo esta
definida hacia `Bucharest`. Greedy tampoco coincidió con A*: siguió una ruta de
884 km, mientras que A* encontró una ruta de 805 km. El patrón se mantiene:
Greedy mira cercania estimada; A* equilibra costo acumulado y estimado restante.
