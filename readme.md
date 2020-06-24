The Nano Center Subscription Bot will manage discord roles and perks for contributing members to The Nano Center.
The amount and length of the subscription are configurable in the .env file

### Nano Repeat
This bot uses Nano Repeat as a service to monitor and verify subscriptions.  There are 2 functions used within the code to handle the entirety of a nano subscription, the `create_subscription` and `verify_subscription` functions located in the `main.py` and `role_update.py` files.  
`mqtt.py` uses MQTT to get real time updates from the system so it can inform users their subscription is active as soon as they pay.

### Initial Dependencies
Your system must have the below dependencies installed to run:
- Python 3.6+
- Redis

### Installation and Configuration
The first thing you need is an account with Nano Repeat.  This is free to setup, just send a POST request to `https://api.nanorepeat.com/signup` with the below information:
```
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@gmail.com",
    "password": "averysecurepassword",
    "forwarding_address": "nano_111pwbptkp6rj6ki3ybmjg4ppg64o9s676frokpydkwrntrnqqfqf84w5kon"
}
```
This will respond with a user ID and token - you must store your token in your .env file for use later.

Second - copy the .exampleenv to .env so the program can load your personal information  
`cp .exampleenv .env`

Third - Change the information to match your data.  
.exampleenv has dummy data as examples, you must delete this and load in your own data to move forward.

Fourth - Create a virtual environment and activate it.  
Make sure you are in the root folder of the project and run the below commands:

`python3 -m venv venv`  
`source venv/bin/activate`

Fifth - Install Dependencies  
In the root directory of the project with the virtual environment active, type:  
`pip install -r requirements.txt`

Sixth - Setup systemctl service  
Copy the exampleservice.service to your systemctl folder  
`cp exampleservice.service /etc/systemd/system/nc-subbot.service`  
Once there, edit the file and update the references in curly braces.  
After you modify the file and save, run the command:  
`sudo systemctl start nc-subbot`  
This will start the service in the background so your bot can run unmonitored.
- NOTE: Any time you want to make a change, you must restart your service `sudo systemctl restart nc-subbot`
- NOTE: You can check the status of the bot by typing `sudo systemctl status nc-subbot`

Seven - Setup cronjob to review roles once a day  
Every day the roles should be checked to see if anyone's subscription has lapsed, or a new subscription was paid that needs a role.  
Cron jobs run periodically scheduled by adding a line like what is in `examplecron` to the command `crontab -e`  
Copy the data from `examplecron` and modify the curly braces to go to the correct folders.

Questions about this bot and implementation can be raised to The Nano Center: https://nanocenter.org/