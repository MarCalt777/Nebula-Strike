# Nebula Strike 🚀

**Nebula Strike** ir aizraujoša 2D kosmosa (Space Shooter) spēle, kas izstrādāta ar Python un **Pygame** bibliotēku. Spēle ir integrēta ar paša izveidotu **FastAPI** REST API serveri un **SQLite** datubāzi, kas nodrošina drošu spēlētāju reģistrāciju, autorizāciju ar tokeniem, rezultātu saglabāšanu un dinamiskas HTML/CSS mājaslapas (līderu tabula, spēlētāja profils un noteikumi) izmantojot **Jinja2** veidnes.

---

## 🛠️ Tehnoloģijas un rīki

* **Valoda:** Python 3.11+
* **Spēles dzinējs:** Pygame
* **Serveris:** FastAPI & Uvicorn
* **Datubāze:** SQLite (ar parametrizētiem SQL vaicājumiem)
* **Validācija & Drošība:** Pydantic, SHA-256 paroļu hashošana, Token-based autentifikācija
* **Mājaslapa:** Jinja2 veidnes, HTML5, CSS3
* **Saziņa:** Requests (klienta daļā)

---

## 📥 Instalēšana un palaišana

Seko šiem soļiem, lai palaistu projektu savā datorā:

### 1. Klonē repozitoriju un atver mapi
```bash
git clone https://github.com/MarCalt777/Nebula-Strike
cd Nebula-Strike
```

### 2. Izveido un aktivizē virtuālo vidi (`venv`)
* **Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalē nepieciešamās bibliotēkas
```bash
pip install -r requirements.txt
```

### 4. Palaid REST API serveri
Atver pirmo termināla logu un palaid serveri:
```bash
uvicorn api.main:app --reload
```
*Mājaslapa un līderu tabula tagad ir pieejama pārlūkprogrammā: **http://127.0.0.1:8000/***

### 5. Palaid spēli
Atver otru termināla logu, aktivizē `venv` un palaid spēles klientu:
```bash
python -m client.Main
```

---

## 🎮 Spēles noteikumi un vadība

### Mērķis
Izdzīvot kosmosa viļņos, iznīcināt ienaidnieku kuģus un izvairīties no asteroīdiem, lai iegūtu pēc iespējas vairāk punktu un iekļūtu Top-10 līderu tabulā.

### Vadība (Controls)
* **Galvenā izvēlne:** Ievadi savu vārdu un spied **`ENTER`**, lai reģistrētos un sāktu spēli.
* **Kustība:** 
  * **`W`** – Pārvietoties augšup
  * **`S`** – Pārvietoties lejup
  * **`A`** – Pārvietoties pa kreisi
  * **`D`** – Pārvietoties pa labi
* **Šaušana:** Kreisais peles klikšķis (**LMB**) – parastā šaušana.
* **Speciālā spēja (Lāzers):** Labais peles klikšķis (**RMB**) – kad speciālā skala ir uzlādēta (pēc 5 iznīcinātiem ienaidniekiem), aktivizē spēcīgu lāzeru!
* **Pauze:** Spied **`P`**, lai nopauzētu spēli, un **`L`**, lai izietu.
* **Pēc spēles beigām (Game Over):** Spied **`R`**, lai sāktu no jauna, vai **`ESC`**, lai izietu.

---

## 🌟 Unikālās mehānikas

1. **Dinamiskā speciālā spēja (Lāzers):** Iznīcinot ienaidniekus, uzlādējas speciālā skala (līdz 5 punktiem). To aktivizējot ar peles labo klikšķi, uz laiku tiek izšauts jaudīgs lāzers, kas neatkarīgi no pretinieka veselības (HP) momentāli iznīcina visus ceļā sastaptos ienaidniekus un lodes.
2. **Uzlabojumu (Power-ups) sistēma:** Ienaidnieki nejauši nomet trīs veidu bonusus:
   * 🟢 **Zaļais:** +1 dzīvība.
   * 🔵 **Zilais:** Aktivizē aizsargvairogu uz laiku, kas bloķē gan pretinieku lodes, gan asteroīdus.
   * 🟠 **Oranžais:** Ieslēdz paātrināto šaušanu uz 5 sekundēm (nav nepieciešams klikšķināt, pietiek turēt nospiestu peles pogu).

---

## 📡 REST API Endpointu tabula

| Metode | Adrese | Apraksts | Veiksmīgs atbildes kods |
| :--- | :--- | :--- | :--- |
| **POST** | `/register` | Reģistrē jaunu spēlētāju (saglabā hashotu paroli) | `201` |
| **POST** | `/login` | Autentificē spēlētāju un atgriež piekļuves tokenu | `200` |
| **POST** | `/scores` | Saglabā spēlētāja rezultātu (pieprasījumā jābūt tokenam) | `201` |
| **GET** | `/scores/top` | Atgriež Top-10 labākos spēlētājus un punktus JSON formātā | `200` |
| **GET** | `/players/{name}/stats` | Atgriež konkrētā spēlētāja statistiku (spēļu skaits, labākais rezultāts) JSON formātā | `200` / `404` |
| **GET** | `/` | Atgriež līderu tabulas HTML lapu (ar Jinja2 veidnēm) | `200` |
| **GET** | `/rules` | Atgriež spēles noteikumu un mehāniku HTML lapu | `200` |
| **GET** | `/players/{name}` | Atgriež konkrētā spēlētāja profilu ar statistiku (HTML lapa) | `200` / `404` |
