# Mögliche Plots aus den Anfragen und Beantwortungen

Basierend auf den Dateinamen (und angenommen, dass die Inhalte der PDFs diese widerspiegeln) lassen sich folgende Visualisierungen erstellen:

## Zeitliche Verteilungen

1.  **Anzahl der Anfragen pro Jahr/Monat/Tag:**
    *   **Warum?** Zeigt Trends in der Anzahl der Anfragen über die Zeit. Hilft, Spitzen und Rückgänge zu identifizieren (z.B. saisonale Schwankungen, Auswirkungen von Ereignissen).
    *   **Datengrundlage:** Datumsteil der Dateinamen in beiden Ordnern (`Anfragen` und `Beantwortungen`).
    *   **Plot-Typ:** Liniendiagramm oder Balkendiagramm.

2.  **Anzahl der Beantwortungen pro Jahr/Monat/Tag:**
    *   **Warum?** Analog zu 1., aber für Beantwortungen. Kann mit 1. verglichen werden, um Verzögerungen oder Rückstände zu erkennen.
    *   **Datengrundlage:** Datumsteil der Dateinamen in beiden Ordnern.
    *   **Plot-Typ:** Liniendiagramm oder Balkendiagramm.

3.  **Zeitdifferenz zwischen Anfrage und Beantwortung:**
    *   **Warum?** Zeigt, wie lange es dauert, bis Anfragen beantwortet werden. Kann als Histogramm oder Boxplot dargestellt werden, um die Verteilung und Ausreißer zu zeigen.
    *   **Datengrundlage:** Datumsdifferenz zwischen korrespondierenden Dateien in `Anfragen` und `Beantwortungen` (basierend auf den INR-Nummern).
    *   **Plot-Typ:** Histogramm, Boxplot, Violinplot.

## INR-Nummern

4.  **Verteilung der INR-Nummern (Histogramm):**
    *   **Warum?** Könnte Hinweise auf die Art und Weise geben, wie INR-Nummern vergeben werden (z.B. fortlaufend, Blöcke, etc.).
    *   **Datengrundlage:** INR-Nummern aus den Dateinamen.
    *   **Plot-Typ:** Histogramm.

5.  **INR-Nummern im Zeitverlauf:**
    *   **Warum?** Zeigt, ob die INR-Nummern chronologisch vergeben werden und ob es Lücken oder Sprünge gibt.
    *   **Datengrundlage:** INR-Nummern und Datum aus den Dateinamen.
    *   **Plot-Typ:** Streudiagramm (Scatterplot) mit Datum auf der x-Achse und INR auf der y-Achse.

## Kombinationen und weitere Analysen (erfordern wahrscheinlich Textextraktion aus PDFs)

Wenn man den Inhalt der PDFs extrahiert (z.B. mit OCR), könnte man zusätzlich folgende Analysen durchführen:

6.  **Häufigste Themen/Schlagwörter in Anfragen:**
    *   **Warum?** Zeigt, welche Themen am häufigsten nachgefragt werden. Hilft, Ressourcen zu priorisieren und FAQs zu erstellen.
    *   **Datengrundlage:** Textextraktion aus den PDFs im `Anfragen`-Ordner.
    *   **Plot-Typ:** Wordcloud, Balkendiagramm der Top-N-Themen.

7.  **Häufigste Themen/Schlagwörter in Beantwortungen:**
     *   **Warum?** Analog zu 6., aber für Beantwortungen.
    *   **Datengrundlage:** Textextraktion aus den PDFs im `Beantwortungen`-Ordner.
    *   **Plot-Typ:** Wordcloud, Balkendiagramm.

8.  **Sentiment-Analyse der Anfragen/Beantwortungen:**
    *   **Warum?** Kann zeigen, ob Anfragen eher positiv, negativ oder neutral formuliert sind. Kann auch für Beantwortungen durchgeführt werden.
    *   **Datengrundlage:** Textextraktion und Sentiment-Analyse-Tools.
    *   **Plot-Typ:** Balkendiagramm (Anteil positiv/negativ/neutral), Zeitreihe des Sentiments.

9.  **Beziehung zwischen Themen und Bearbeitungszeit:**
    *   **Warum?** Könnte zeigen, ob bestimmte Themen länger dauern, um beantwortet zu werden.
    *   **Datengrundlage:** Textextraktion, Themenklassifizierung und Zeitdifferenz (siehe 3.).
    *   **Plot-Typ:** Boxplots (Bearbeitungszeit pro Thema), Streudiagramm.

10. **Netzwerkanalyse der Anfragen und Beantwortungen**
    *   **Warum?** Wenn in den Dokumenten Referenzen oder Beziehungen zwischen Anfragen/Beantwortungen existieren, könnte eine Netzwerkanalyse diese Beziehungen visualisieren.
    *   **Datengrundlage:** Textextraktion und Identifikation von Beziehungen.
    *   **Plot-Typ:** Netzwerkdiagramm.

**Wichtiger Hinweis:** Die Punkte 6-10 setzen voraus, dass der Text aus den PDFs extrahiert und verarbeitet werden kann. Dies ist ein zusätzlicher Schritt, der je nach Qualität der PDFs (z.B. gescannte Dokumente vs. digital erzeugte PDFs) unterschiedlich komplex sein kann. 