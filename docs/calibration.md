# Kalibrierung

Der wichtigste Kalibrierwert im Arduino-Code ist:

```cpp
float Stepsprograd = 65.75;
```

Dieser Wert bedeutet:

```text
Motorschritte pro 1 Grad Drehtellerbewegung
```

Wenn der Drehteller nicht exakt auf den gewünschten Winkel fährt, muss dieser Wert angepasst werden.

## Wovon hängt der Wert ab?

- Motor-Schrittzahl, z. B. 200 Schritte pro Umdrehung
- Microstepping am TB6600
- Zahnrad / Ritzel
- Drehkranz-Übersetzung
- mechanisches Spiel

## Einfache Kalibrierung

1. Drehteller referenzieren lassen.
2. Einen gut messbaren Winkel anfahren, z. B. `90°`.
3. Tatsächlichen Winkel messen.
4. Neuen Wert berechnen:

```text
neuer Stepsprograd = alter Stepsprograd × Sollwinkel / Istwinkel
```

## Beispiel

Der aktuelle Wert ist:

```text
65.75
```

ARTA fordert an:

```text
90°
```

Der Teller fährt tatsächlich nur:

```text
87°
```

Dann:

```text
65.75 × 90 / 87 = 68.02
```

Der neue Wert wäre also:

```cpp
float Stepsprograd = 68.02;
```

## Empfehlung

Nach der Korrektur mehrere Winkel prüfen:

- 15°
- 30°
- 45°
- 90°
- 180°

Wenn kleine Abweichungen je nach Richtung auftreten, liegt wahrscheinlich mechanisches Spiel vor. Dann hilft:

- Ritzelspiel reduzieren,
- Zahnkranz prüfen,
- immer aus derselben Richtung referenzieren,
- Beschleunigung/Geschwindigkeit reduzieren.
