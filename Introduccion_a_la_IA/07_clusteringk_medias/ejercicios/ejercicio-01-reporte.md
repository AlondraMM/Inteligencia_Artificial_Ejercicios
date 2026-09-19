# Reporte

## Resultados del ejercicio 1: Cambiar los centros

En los datos originales, tres centros se encuentran muy próximos, por lo que K-Means puede confundirlos y agrupar algunas observaciones en un mismo cluster. Al aumentar la separación entre los centros, los cinco grupos se vuelven más distinguibles. Esto se refleja en el método del codo, donde la reducción de la inercia se vuelve más gradual después de (k=5), y en el score de silueta, cuyo valor máximo se obtiene con (k=5) (aprox. 0.80). Ambas métricas respaldan la existencia de cinco grupos bien separados.

## Resultados de aumentar las desviaciones estándar 

Al aumentar las desviaciones estándar, los grupos presentan mayor dispersión y, por lo tanto, mayor solapamiento. Esto dificulta que K-Means identifique claramente los clusters. El método del codo sugiere aproximadamente (k=4), mientras que el score de silueta presenta valores relativamente cercanos entre (k=2) y (k=4). Esto indica que la estructura de los grupos es menos evidente cuando aumenta la dispersión.

## Resultados de kmeans en una imagen

K-Means puede utilizarse para reducir el número de colores de una imagen agrupando píxeles con valores RGB similares. Con 10 y 8 colores la diferencia visual es pequeña; con 6 colores todavía se distinguen elementos como el mar, mientras que con 4 colores aumenta la pérdida de detalle y resulta más difícil diferenciar elementos como la persona, las piedras, el mar y el cielo. Con menos clusters se obtiene una imagen más simple, pero a costa de perder información visual.

## Resultados de kmeans en una Iris

En el conjunto Iris, K-Means identifica una estructura de tres grupos, aunque el algoritmo no utiliza las etiquetas de las especies. El método del codo sugiere (k=3), mientras que el score de silueta presenta valores altos para (k=2) y (k=3). Esto muestra que tres clusters representan razonablemente la estructura del conjunto, aunque algunos grupos presentan mayor separación que otros.

En conclusión, el desempeño de K-Means depende de la estructura geométrica de los datos. La separación entre centros, la dispersión de los grupos y el número de clusters influyen directamente en la capacidad del algoritmo para recuperar grupos bien definidos.