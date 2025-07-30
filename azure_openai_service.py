import os
import base64
from openai import AzureOpenAI
import logging

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    def __init__(self):
        self.endpoint = os.getenv("ENDPOINT_URL", "https://aifoundry-bundai-101.cognitiveservices.azure.com/")
        self.deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4.1-mini")
        self.subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        
        if not self.subscription_key or self.subscription_key == "REPLACE_WITH_YOUR_KEY_VALUE_HERE":
            logger.warning("Azure OpenAI API key not configured. Using fallback responses.")
            self.client = None
        else:
            try:
                # Initialize Azure OpenAI client with key-based authentication
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.subscription_key,
                    api_version="2025-01-01-preview",
                )
                logger.info("Azure OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI client: {e}")
                self.client = None

    def get_it_support_response(self, user_message, chat_history=None):
        """
        Get an enhanced IT support response using Azure OpenAI
        """
        if not self.client:
            # Fallback to basic keyword-based responses if no LLM available
            return self._get_fallback_response(user_message)
        
        try:
            # Prepare the system prompt for IT support
            system_prompt = """Sie sind ein professioneller IT-Support-Assistent für ein deutsches Unternehmen. 
            Ihre Aufgabe ist es, technische Probleme zu lösen und Schritt-für-Schritt-Anleitungen zu geben.

            Anweisungen:
            - Antworten Sie immer auf Deutsch
            - Seien Sie präzise und hilfreich
            - Geben Sie konkrete, umsetzbare Schritte
            - Bei komplexen Problemen empfehlen Sie den Kontakt zur IT-Abteilung
            - Seien Sie freundlich und professionell
            - Strukturieren Sie Ihre Antworten mit nummerierten Listen
            - Erwähnen Sie bei Hardware-Problemen auch Sicherheitshinweise

            Häufige IT-Bereiche:
            - Computer-Probleme (Start, Performance, Fehler)
            - E-Mail und Outlook-Probleme
            - Drucker und Peripheriegeräte
            - Netzwerk und VPN-Verbindungen
            - Software-Installation und Updates
            - Passwort-Zurücksetzung
            """

            # Build chat history for context
            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": system_prompt}]
                }
            ]

            # Add chat history if available
            if chat_history:
                for entry in chat_history[-5:]:  # Last 5 messages for context
                    role = "user" if entry['sender'] == 'user' else "assistant"
                    messages.append({
                        "role": role,
                        "content": [{"type": "text", "text": entry['message']}]
                    })

            # Add current user message
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": user_message}]
            })

            # Generate the completion
            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=800,
                temperature=0.3,  # Lower temperature for more consistent IT support
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False
            )

            response = completion.choices[0].message.content
            logger.info(f"Generated Azure OpenAI response for: {user_message[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error calling Azure OpenAI API: {e}")
            return self._get_fallback_response(user_message)

    def _get_fallback_response(self, user_message):
        """
        Fallback response when Azure OpenAI is not available
        """
        message_lower = user_message.lower()
        
        # Enhanced keyword-based responses with better structure
        if any(word in message_lower for word in ['computer', 'pc', 'rechner', 'start', 'boot', 'hochfahren']):
            return """🖥️ **Computer-Startprobleme - Lösungsschritte:**

1. **Stromversorgung prüfen:**
   - Ist das Netzkabel richtig eingesteckt?
   - Leuchtet die Stromled am Computer?

2. **Hardware-Check:**
   - Alle Kabel (Monitor, Tastatur, Maus) überprüfen
   - RAM-Module neu einstecken (bei Desktop-PCs)

3. **Neustart versuchen:**
   - Computer vollständig ausschalten (30 Sekunden warten)
   - Wieder einschalten

4. **Erweiterte Optionen:**
   - F8 beim Start drücken für Startoptionen
   - Abgesicherter Modus versuchen

**Wenn das Problem weiterhin besteht:** Kontaktieren Sie die IT-Abteilung unter Durchwahl 1234 mit der genauen Fehlermeldung."""

        elif any(word in message_lower for word in ['email', 'e-mail', 'outlook', 'mail']):
            return """📧 **E-Mail-Probleme - Schritt-für-Schritt-Lösung:**

1. **Internetverbindung testen:**
   - Können Sie andere Websites öffnen?
   - WLAN/LAN-Verbindung überprüfen

2. **Outlook neu starten:**
   - Outlook vollständig schließen
   - Warten Sie 30 Sekunden
   - Outlook erneut öffnen

3. **E-Mail-Einstellungen prüfen:**
   - Datei → Kontoeinstellungen → Kontoeinstellungen
   - "Kontoeinstellungen testen" klicken

4. **Postfach-Größe überprüfen:**
   - Sind Sie innerhalb des Speicherlimits?
   - Alte E-Mails archivieren

**Bei Passwort-Problemen:** Wenden Sie sich an die IT für eine Passwort-Zurücksetzung."""

        elif any(word in message_lower for word in ['drucker', 'printer', 'drucken', 'print']):
            return """🖨️ **Drucker-Probleme - Fehlerbehebung:**

1. **Grundlegende Überprüfung:**
   - Ist der Drucker eingeschaltet?
   - USB/Netzwerkkabel richtig verbunden?
   - Genug Papier und Toner/Tinte?

2. **Druckwarteschlange leeren:**
   - Windows: Einstellungen → Drucker & Scanner
   - Drucker auswählen → "Warteschlange öffnen"
   - Alle Aufträge löschen

3. **Drucker neu starten:**
   - Drucker ausschalten (30 Sekunden warten)
   - Wieder einschalten
   - Testseite drucken

4. **Treiber aktualisieren:**
   - Geräte-Manager öffnen
   - Drucker suchen → Rechtsklick → "Treiber aktualisieren"

**Bei Papierstau:** Schalten Sie den Drucker aus, bevor Sie Papier entfernen!"""

        elif any(word in message_lower for word in ['passwort', 'password', 'login', 'anmeldung']):
            return """🔐 **Passwort-Probleme - Sofortige Hilfe:**

1. **Passwort-Zurücksetzung:**
   - Kontaktieren Sie die IT-Hotline: **Durchwahl 1234**
   - Halten Sie Ihren Personalausweis bereit
   - Temporäres Passwort wird erstellt

2. **Caps Lock prüfen:**
   - Ist die Feststelltaste aktiviert?
   - Wird das richtige Tastaturlayout verwendet?

3. **Passwort-Richtlinien beachten:**
   - Mindestens 8 Zeichen
   - Großbuchstaben, Kleinbuchstaben, Zahlen
   - Sonderzeichen verwenden

4. **Sicherheitstipps:**
   - Passwort nicht aufschreiben
   - Regelmäßig ändern (alle 90 Tage)
   - Nicht mit anderen teilen

**Wichtig:** Bei gesperrtem Konto sofort IT kontaktieren!"""

        else:
            return """🛠️ **Allgemeine IT-Unterstützung:**

Vielen Dank für Ihre Anfrage! Hier sind die ersten Schritte zur Problemlösung:

1. **Computer neu starten** - Löst 80% aller Probleme
2. **Alle Kabelverbindungen überprüfen**
3. **Software-Updates installieren**
4. **Antivirus-Scan durchführen**

**Für spezielle Hilfe kontaktieren Sie:**
- 📞 IT-Hotline: **Durchwahl 1234**
- 📧 E-Mail: it-support@firma.com
- 🕐 Verfügbar: Mo-Fr, 8:00-17:00 Uhr

**Bitte beschreiben Sie Ihr Problem genauer, damit ich Ihnen besser helfen kann!**

Mögliche Bereiche: Computer-Probleme, E-Mail-Probleme, Drucker-Probleme, Passwort-Zurücksetzung"""

# Global instance
azure_openai_service = AzureOpenAIService()
