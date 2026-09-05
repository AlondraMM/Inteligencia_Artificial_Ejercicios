# Ejercicio 1 — Reporte 

## Diagrama de la cueva:

```text
4 | .  P  .  .
3 | .  G  .  P
2 | .  .  .  W
1 | A> .  .  P

    1  2  3  4
```
## Reporte de resultados

El agente de reflejo simple falla porque no tiene memoria ni objetivo. En este mapa avanza hasta [3,1], percibe brisa por el pit en [4,1], y su regla fija ante brisa es girar a la derecha; como la percepción no cambia al girar, se queda rotando hasta agotar los 200 pasos. En cambio, los agentes basado en modelo, basado en metas y basado en utilidad sí usan conocimiento acumulado para moverse por casillas seguras y regresar con el oro. El agente basado en utilidad lo hace con menos pasos porque evalúa planes por puntaje esperado.

Si se acerca un pit a la casilla inicial, por ejemplo a [2,1] o [1,2], el agente basado en modelo recibe brisa desde el inicio y deja de poder demostrar que sus vecinos son seguros, así que tiende a quedarse girando en lugar de arriesgarse. Si se aleja ese pit, aparecen más casillas inferidas como seguras y el agente puede explorar con mucha más facilidad.
