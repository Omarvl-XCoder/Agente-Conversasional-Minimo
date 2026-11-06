"""
SCRUM-36: Pruebas locales del modulo Bayes (bayes_router.py).

Ejecutar desde la carpeta Backend, sin Docker:
    python test_bayes.py

Mide la precision con mensajes que NO estan en los datos de entrenamiento.
"""
import unittest
from collections import Counter

from bayes_router import clasificador, DATOS_ENTRENAMIENTO

INTENCIONES = ["info_fatiga", "alerta_flotilla", "fuera_de_dominio"]

# (intencion esperada, mensaje) -- ninguno esta en DATOS_ENTRENAMIENTO
CASOS_PRUEBA = [
    ("info_fatiga", "¿Cuáles son las señales de que un chofer está cansado?"),
    ("info_fatiga", "¿Cuántas horas de descanso necesita un conductor?"),
    ("info_fatiga", "Dime cómo evitar quedarme dormido al volante"),
    ("info_fatiga", "¿Qué es un microsueño?"),
    ("info_fatiga", "¿Por qué la somnolencia es peligrosa en carretera?"),
    ("info_fatiga", "Explícame la diferencia entre cansancio y fatiga"),
    ("alerta_flotilla", "La unidad 12 generó una alerta de parpadeo"),
    ("alerta_flotilla", "El conductor del tráiler lleva horas bostezando, ¿qué hago?"),
    ("alerta_flotilla", "Se activó el sensor de desviación de carril en el camión 3"),
    ("alerta_flotilla", "Reporte de alertas de hoy en la flotilla"),
    ("alerta_flotilla", "Mi operador tiene cabeceo en el turno nocturno"),
    ("alerta_flotilla", "Alerta de fatiga en la unidad 7"),
    ("fuera_de_dominio", "¿Cuál es la capital de Japón?"),
    ("fuera_de_dominio", "Dame una receta de tacos"),
    ("fuera_de_dominio", "¿Quién ganó el partido de ayer?"),
    ("fuera_de_dominio", "Cuéntame un chiste"),
    ("fuera_de_dominio", "¿Cuánto cuesta una laptop?"),
    ("fuera_de_dominio", "Ayúdame con mi tarea de física"),
]

PRECISION_MINIMA = 0.60  # guarda contra regresiones; subirla al mejorar el modelo


class TestBayes(unittest.TestCase):

    def test_probabilidades_suman_uno(self):
        for _, m in CASOS_PRUEBA:
            r = clasificador.clasificar(m)
            self.assertAlmostEqual(sum(r["probabilidades"].values()), 1.0, delta=0.01)

    def test_mensaje_sin_palabras_conocidas_es_incierto(self):
        r = clasificador.clasificar("xyzzy qwerty")
        self.assertEqual(r["intencion"], "incierto")
        for p in r["probabilidades"].values():
            self.assertAlmostEqual(p, 1 / 3, delta=0.01)  # solo pesan los priors

    def test_acentos_y_mayusculas_no_cambian_resultado(self):
        a = clasificador.clasificar("¿QUÉ ES LA SOMNOLENCIA AL CONDUCIR?")
        b = clasificador.clasificar("que es la somnolencia al conducir")
        self.assertEqual(a["intencion"], b["intencion"])

    def test_datos_de_entrenamiento_se_clasifican_bien(self):
        for intencion, frases in DATOS_ENTRENAMIENTO.items():
            for f in frases:
                self.assertEqual(clasificador.clasificar(f)["intencion"], intencion, f)

    def test_casos_clave(self):
        esperados = {
            "La unidad 5 tiene una alerta de parpadeo": "alerta_flotilla",
            "¿Qué es la somnolencia al conducir?": "info_fatiga",
        }
        for m, esp in esperados.items():
            self.assertEqual(clasificador.clasificar(m)["intencion"], esp, m)

    def test_nunca_enruta_con_seguridad_a_la_intencion_equivocada(self):
        """Un error aceptable es 'incierto'; uno grave es decidir mal."""
        graves = [
            (esp, m) for esp, m in CASOS_PRUEBA
            if clasificador.clasificar(m)["intencion"] not in (esp, "incierto")
        ]
        self.assertEqual(graves, [], f"Clasificaciones equivocadas: {graves}")

    def test_precision_minima(self):
        aciertos = sum(clasificador.clasificar(m)["intencion"] == e for e, m in CASOS_PRUEBA)
        self.assertGreaterEqual(aciertos / len(CASOS_PRUEBA), PRECISION_MINIMA)


def reporte():
    print("\n" + "=" * 64)
    print("REPORTE DE PRECISION (mensajes fuera del entrenamiento)")
    print("=" * 64)
    aciertos = 0
    por_clase = {i: [0, 0] for i in INTENCIONES}  # [aciertos, total]
    matriz = Counter()
    fallos = []
    for esp, m in CASOS_PRUEBA:
        r = clasificador.clasificar(m)
        ok = r["intencion"] == esp
        aciertos += ok
        por_clase[esp][1] += 1
        por_clase[esp][0] += ok
        matriz[(esp, r["intencion"])] += 1
        if not ok:
            fallos.append((esp, r["intencion"], r["confianza"], m, r["palabras_usadas"]))

    print(f"\nPrecision global: {aciertos}/{len(CASOS_PRUEBA)} = {aciertos/len(CASOS_PRUEBA):.0%}")
    print("\nPor intencion:")
    for i, (a, t) in por_clase.items():
        print(f"  {i:<18} {a}/{t} = {a/t:.0%}")

    cols = INTENCIONES + ["incierto"]
    print("\nMatriz de confusion (fila = esperado, columna = obtenido):")
    print(" " * 18 + "".join(f"{c[:12]:>14}" for c in cols))
    for f in INTENCIONES:
        print(f"{f:<18}" + "".join(f"{matriz[(f, c)]:>14}" for c in cols))

    if fallos:
        print("\nFallos:")
        for esp, obt, conf, m, pal in fallos:
            print(f"  esperado={esp} obtenido={obt} (conf {conf}) | {m!r} | palabras={pal}")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    reporte()
    unittest.main(verbosity=2)
