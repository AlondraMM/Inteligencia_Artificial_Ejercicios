# Reporte

## Resultados comparados

Se compararon las 30 corridas de `01_Multilayer_perceptron.ipynb` y
`02_Keras_multilayer_perceptron_iris.ipynb`. En ambas notebooks se entrenaron
dos arquitecturas: la original `4 x 3 x 3` y la profunda
`4 x 3 x 3 x 3 x 3`. Se mantuvieron sigmoide, MSE, SGD, `eta = 0.03` y 500
epocas.

| Implementación | Topología | Error/loss medio final | Desv. est. | Min | Max | Accuracy media |
|---|---|---:|---:|---:|---:|---:|
| NumPy | `4 x 3 x 3` | 0.060084 | 0.005701 | 0.056694 | 0.089609 | 0.9660 |
| NumPy | `4 x 3 x 3 x 3 x 3` | 0.378192 | 0.197943 | 0.095046 | 0.671364 | 0.6647 |
| Keras | `4 x 3 x 3` | 0.166381 | 0.025838 | 0.130981 | 0.222563 | 0.6480 |
| Keras | `4 x 3 x 3 x 3 x 3` | 0.221619 | 0.001150 | 0.217927 | 0.222614 | 0.3678 |

## Análisis

Al añadir dos capas, el error no bajó más; empeoró en ambas implementaciones.
En NumPy, la red original fue muy estable: casi todas las corridas terminaron
con error cercano a `0.06` y accuracy alrededor de `0.966`. La red profunda
tuvo mucha variabilidad: algunas semillas llegaron a errores razonables
(`0.095046` fue el mejor caso), pero muchas se quedaron cerca de `0.67`, con
accuracy de `0.3333`. En promedio, la red profunda NumPy fue claramente peor:
`0.378192` contra `0.060084`.

En Keras paso algo parecido, pero con otro matiz. La red original tuvo loss
medio `0.166381`, mientras que la profunda quedo en `0.221619`. La desviación
estandar de la red profunda fue muy baja (`0.001150`), pero eso no significa
que haya sido buena: significa que casi siempre se estancó.
Su accuracy media fue `0.3678`, muy cerca del azar para tres clases. En cambio,
la red original de Keras fue menos precisa que la NumPy original, pero aun así
superó claramente a su versión profunda.

Las curvas de NumPy y Keras no se parecen mucho con la misma topología. Para
`4 x 3 x 3`, NumPy baja mas y con mucha estabilidad; Keras baja de forma más
suave y se queda en una perdida mayor. Esto puede explicarse por diferencias de
inicializacioón, orden de datos, actualización de pesos ejemplo por ejemplo
frente al entrenamiento por lotes de Keras, vectorización, convenciones exactas
del MSE y detalles del optimizador. Aunque conceptualmente ambas redes usan
sigmoide, MSE y SGD, no son ejecuciones idénticas.

Con sigmoides apiladas y MSE tiene sentido que una red más profunda no aprenda
mejor en Iris. Iris es un conjunto pequeño, de 150 ejemplos, y una arquitectura
simple ya puede capturar gran parte de la separación entre clases. Al agregar
capas sigmoides, las derivadas pueden hacerse pequenas y el gradiente se
debilita al retropropagarse. Las graficas y las 30 corridas reflejan eso: la
red profunda de Keras casi no sale del loss `~0.222`, y la profunda
de NumPy depende mucho de la semilla. En este experimento, más profundidad
agregó inestabilidad y dificultad de optimización, no una mejora real.

## ReLU, softmax y capas más anchas

Después se repitió la red profunda en Keras cambiando la función de activación
de las capas ocultas a `ReLU`, la salida a `softmax` y la pérdida a
`categorical_crossentropy`. Además, se probó una versión más ancha con tres
capas ocultas de 8 neuronas. Estos resultados corresponden a una corrida del
reto con división entrenamiento/prueba estratificada.

| Modelo | Capas ocultas | Activación / pérdida | Train loss | Val loss | Train accuracy | Test accuracy | F1 ponderado | Brecha train-test |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Deep sigmoid MSE | `3 x 3 x 3` | Sigmoid + MSE | 0.222366 | 0.222351 | 0.3333 | 0.3333 | 0.1667 | 0.0000 |
| Deep ReLU softmax | `3 x 3 x 3` | ReLU + crossentropy | 1.098825 | 1.098685 | 0.3333 | 0.3333 | 0.1667 | 0.0000 |
| Wide ReLU softmax | `8 x 8 x 8` | ReLU + crossentropy | 0.067387 | 0.095511 | 0.9833 | 0.9333 | 0.9327 | 0.0500 |

La red profunda angosta con `ReLU + softmax` no mejoró frente a la versión
todo-sigmoide con MSE: ambas quedaron en `0.3333` de accuracy, que equivale a
clasificar prácticamente al azar entre tres clases. En ese caso, cambiar la
activación y la pérdida no fue suficiente; la topología `4 x 3 x 3 x 3 x 3`
parece demasiado limitada o difícil de optimizar para esta configuración.

La diferencia importante apareció al aumentar las neuronas ocultas a
`4 x 8 x 8 x 8 x 3`. Esa red sí aprendió el patrón de Iris: alcanzó `0.9833`
en entrenamiento y `0.9333` en prueba, con F1 ponderado de `0.9327`. La brecha
de `0.05` entre entrenamiento y prueba sugiere un ligero sobreajuste, pero no
un sobreajuste severo en esta corrida. En conclusión, Iris sí se benefició de
una red más ancha cuando se usó una formulación más adecuada para clasificación
multiclase (`softmax + categorical_crossentropy`), aunque por el tamaño pequeño
del dataset conviene revisar estabilidad con varias semillas para confirmar que
la mejora no dependa de una sola partición o inicialización.
