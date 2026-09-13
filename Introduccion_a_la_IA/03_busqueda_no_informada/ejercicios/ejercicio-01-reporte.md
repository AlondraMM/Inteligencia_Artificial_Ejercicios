# Reporte - Búsqueda no informada en el mapa de Rumania

## Pareja elegida

- Origen: `Timisoara`
- Destino: `Bucharest`

Esta pareja es distinta del caso por defecto `Arad -> Bucharest` y permite ver
una diferencia clara entre BFS y UCS: BFS encuentra una ruta con menos
carreteras, mientras que UCS encuentra una ruta con menor distancia total.

## Diagrama del subgrafo relevante

Todas las carreteras son bidireccionales y los pesos están en kilómetros.

```text
Timisoara --118-- Arad --140-- Sibiu --99-- Fagaras --211-- Bucharest
                                  |
                                  80
                                  |
                           Rimnicu Vilcea --97-- Pitesti --101-- Bucharest
```

## Tabla comparativa

| Algoritmo | Status | Path | Depth | Cost | Expanded | Generated |
|---|---|---|---:|---:|---:|---:|
| BFS | success | Timisoara -> Arad -> Sibiu -> Fagaras -> Bucharest | 4 | 568 km | 7 | 17 |
| UCS | success | Timisoara -> Arad -> Sibiu -> Rimnicu Vilcea -> Pitesti -> Bucharest | 5 | 536 km | 12 | 31 |
| DFS | success | Timisoara -> Arad -> Sibiu -> Fagaras -> Bucharest | 4 | 568 km | 4 | 12 |
| DLS, limit 3 | cutoff | - | - | - | 6 | 16 |
| DLS, limit 4 | success | Timisoara -> Arad -> Sibiu -> Fagaras -> Bucharest | 4 | 568 km | 4 | 6 |
| IDS | success | Timisoara -> Arad -> Sibiu -> Fagaras -> Bucharest | 4 | 568 km | 14 | 34 |

## Análisis

BFS sí encontró el camino con menos carreteras: su solución tiene profundidad 4
(`Timisoara -> Arad -> Sibiu -> Fagaras -> Bucharest`). Como BFS expande por
niveles, la primera solución encontrada es óptima en número de aristas, pero no
necesariamente en kilómetros. En este caso su costo fue de 568 km.

UCS encontró el camino de menor costo acumulado en kilómetros:
`Timisoara -> Arad -> Sibiu -> Rimnicu Vilcea -> Pitesti -> Bucharest`, con
536 km. Aunque esta ruta usa 5 carreteras en vez de 4, evita el tramo largo
`Fagaras -> Bucharest` de 211 km y lo reemplaza por la combinacion
`Rimnicu Vilcea -> Pitesti -> Bucharest`, que resulta más barata en total.
Por eso BFS y UCS discrepan: optimizan criterios distintos.

DFS puede devolver un camino más largo porque explora en profundidad siguiendo
una rama hasta donde pueda antes de probar alternativas. El grafo es el mismo,
pero la estrategia de frontera no compara ni profundidad minima ni costo total.
En esta corrida DFS coincidió con BFS por el orden alfabético de expansión, no
porque DFS tenga garantia de optimalidad.

DLS con `--limit 3` terminó en `cutoff` porque la solución más cercana por
número de carreteras está a profundidad 4. Al subir a `--limit 4`, DLS encontró
la misma ruta de 4 carreteras que BFS. IDS también encontró una solucion a
profundidad 4, coincidiendo con BFS en número de carreteras, aunque expandió más
nodos porque repite búsquedas con límites crecientes hasta llegar al límite
suficiente.

En cuanto a trabajo realizado, UCS expandió 12 nodos y generó 31, más que BFS
(7 expandidos, 17 generados), porque tuvo que mantener y comparar rutas por
costo acumulado antes de poder confirmar la solución más barata.

## Reto opcional

### Caso donde BFS y UCS discrepan

La pareja `Timisoara -> Bucharest` cumple el reto porque BFS y UCS no devuelven
el mismo camino:

| Algoritmo | Camino | Depth | Cost | Expanded | Generated |
|---|---|---:|---:|---:|---:|
| BFS | Timisoara -> Arad -> Sibiu -> Fagaras -> Bucharest | 4 | 568 km | 7 | 17 |
| UCS | Timisoara -> Arad -> Sibiu -> Rimnicu Vilcea -> Pitesti -> Bucharest | 5 | 536 km | 12 | 31 |

BFS trabajó menos en esta instancia si medimos nodos expandidos y generados:
expandió 7 nodos y generó 17. UCS expandió 12 y generó 31, porque tuvo que
seguir comparando alternativas de menor costo antes de asegurar que la ruta de
536 km era la mejor.

### Variación de destino con el mismo origen

Manteniendo el origen `Timisoara` y variando solo el destino para observar el
`--limit` mínimo de DLS,el patrón fue directo: el límite mínimo que permite
encontrar solución coincide con la profundidad del camino encontrado por BFS.

| Origen | Destino | BFS depth | DLS con límite bajo | Primer límite con solución | Camino encontrado por DLS |
|---|---|---:|---|---:|---|
| Timisoara | Lugoj | 1 | `limit=0` -> cutoff | 1 | Timisoara -> Lugoj |
| Timisoara | Drobeta | 3 | `limit=2` -> cutoff | 3 | Timisoara -> Lugoj -> Mehadia -> Drobeta |
| Timisoara | Bucharest | 4 | `limit=3` -> cutoff | 4 | Timisoara -> Arad -> Sibiu -> Fagaras -> Bucharest |
| Timisoara | Eforie | 7 | `limit=6` -> cutoff | 7 | Timisoara -> Arad -> Sibiu -> Fagaras -> Bucharest -> Urziceni -> Hirsova -> Eforie |

Esto muestra la relación entre DLS, BFS e IDS: si el límite de DLS es menor que
la profundidad de la solución más cercana, el resultado es `cutoff`; cuando el
límite alcanza esa profundidad, DLS puede encontrar la ruta. IDS automatiza ese
proceso probando límites crecientes hasta llegar al mínimo suficiente.

