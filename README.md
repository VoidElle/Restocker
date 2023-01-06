# Restocker
![Restock icon](./readme/icon.jpg)

"Restocker" is a Python bot that helps shoe sellers on the online marketplace "Restocks" maximize their profits. By constantly monitoring the prices of similar shoes being sold on the platform, the bot adjusts the prices of a seller's shoes to ensure they are competitive while still being profitable. The bot can be configured to target a specific profit margin or to base pricing decisions on a variety of factors, such as the seller's cost of goods and the current demand for the shoe. With the Restocks Price Manager, sellers can save time and effort by automating the pricing of their shoes, freeing them up to focus on other aspects of their business.

## Features
The current bot features are:
- Automatic decrement of prices to the stop loss price or to the cheapest price at the moment of the bot's run
- If the price reaches the stop loss and at the same time the shoe with the current price becomes the cheapest, instead of remaining at the normal price, its price is set to a backup price, configurable by the bot


## Getting Started

### Prerequisites

This is a list of prerequisites to start Restocker:
* 1920x1080 screen
* Chrome browser
* Python 3
* pip

### Installation

_Below you will find step by step instructions to start Restocker_

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
   You will find your account id using userinfobot in telegram

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
