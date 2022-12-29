# Restocker
![Restock icon](./readme/icon.jpg)

Restocker è un bot automatico per rendere le proprie offerte di sneakers le più economiche possibili sul sito [Restocks](https://restocks.net/).
Il bot è formato in 2 sezioni:
- Pannello di amministrazione utilizzando un bot di telegram per una gestione semplice
- Bot web che permette il decrentamento dei prezzi delle sneakers

## Features
Le features del bot attuali sono:
- Decremento automatico dei prezzi fino al prezzo di stop loss oppure al prezzo più economico nel momento del run del bot
- Se il prezzo raggiunge lo stop loss e allo stesso momento la scarpa con il prezzo attuale diventa la più economica, al posto di rimanere al prezzo normale, il suo prezzo viene impostato ad un prezzo di backup, configurabile dal bot


## Getting Started

### Prerequisites

Questa è una lista dei prerequisiti per avviare Restocker:
* Python 3
* pip

### Installation

_Sotto trovarai le istruzioni passo passo per avviare Restocker_

1. Clone the repository
   ```sh
   git clone https://github.com/VoidElle/Restocker.git
   ```
2. Install the requirements
   ```sh
   pip install -r requirements.txt
   ```
3. Change the Bot Token inside the `telegram_bot.py`
   ```js
   token = "YOUR_TOKEN"
   ``` 
   You can request a bot token using BotFather in telegram
4. Add your user id inside `data/telegram/bot_access.json`
   ```json
     {
        "id": 0
     }
   ```
   You will find your ide using userinfobot in telegram