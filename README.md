# Portable Border Intrusion Detection System (BIDS)

This ESP32-based IoT prototype provides continuous perimeter monitoring by combining motion, vibration, and acoustic sensing with environmental hazard detection.

---

## ## Core Features
**Dual-Layer Detection**: Triggers alerts only when PIR motion is confirmed by vibration or sound to minimize false positives.
**Environmental Sensing**: Monitors temperature, humidity (DHT11), and air quality (MQ135).
**IoT Dashboard**: Real-time data visualization and event logging via the Blynk app.
**Automated Response**: Local audiovisual alarms (Buzzer/LED) and cloud notifications.

---

## ## Hardware Mapping
| Component | Pin | Role |
| **PIR Sensor** | GPIO 13 |Primary Motion |
| **Vibration** | GPIO 12 |Impact/Breach |
| **Sound** | GPIO 34 |Acoustic Trigger  |
| **DHT11** | GPIO 14 | Temp/Humidity |
| **MQ135** | GPIO 35 |Air Quality  |
| **Buzzer/LED** | 27 / 26 | Local Alert  |

---

## ## Setup
1.  **Configure Blynk**: Use Template ID `xxxx` and the provided Auth Token.
2.  **Connectivity**: Update `ssid` and `pass` with your network credentials.
3.  **Deployment**: The system uses India Standard Time (UTC +5:30) for event logging
