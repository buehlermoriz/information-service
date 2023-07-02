# plant-service

Dieser Service ist für die Verbindung zu Datenquellen zuständig und Liefert Informationen zu den Pflanzen, dem Wetter und der Wissensseite.

Um den Service lokal zu nutzen sind folgende Schritte notwendig:
- (optional) Erstellen Sie eine virtuelle Umgebung (venv) über ```python3 -m venv venv``` und aktivieren Sie diese über ```source venv/bin/activate```
- Installieren Sie die benötigten Pakete über ```pip install -r requirements.txt```
- Erstellen Sie eine ```keys.json``` datei im ```.venv``` Ordner, in welcher Sie den API Key für Firebase hinterlegen
- Erstellen Sie eine ```.env``` Datei im Rootverzeichnis, in welcher Sie die API-Keys für OpenAI und Openweathermap hinterlegen
- Starten Sie den Service über ```python3 app.py``` oder über den Pfeil oben rechts in VSCode.
