# Van Systems MQTT Client
A Python script that starts an MQTT client to monitor traffic coming from various microcontrollers that read data from systems in a camper van. Depending on those types of messages it will store data from remote sensors in the database, grab values from the database to transmit to sensors when they connect, or reset values when the water tank is refilled.
Currently this will have a [water sensor](https://github.com/michaelpappas/van_water_meter) with a [GR-301 hall effect](https://www.amazon.com/GRODIA-Connect-Food-Grade-Flowmeter-Counter/dp/B07MY7H45V/?_encoding=UTF8&pd_rd_w=YQrbm&content-id=amzn1.sym.5f7e0a27-49c0-47d3-80b2-fd9271d863ca%3Aamzn1.symc.e5c80209-769f-4ade-a325-2eaec14b8e0e&pf_rd_p=5f7e0a27-49c0-47d3-80b2-fd9271d863ca&pf_rd_r=WGQCKFQMH5ZBEDE2R0SC&pd_rd_wg=zNbva&pd_rd_r=93dfe9cd-b847-4d7c-91f8-26467ed844d3&ref_=pd_gw_ci_mcx_mr_hp_atf_m&th=1) flow meter connected to a Raspberry Pi Zero W and an [ESP-32](https://github.com/michaelpappas/BMS_MQTT_ESP32) that is reading serial communication from a JBD BMS for a DIY LiFePO4 battery.
A flask app is also included to allow for an endpoint that resets water consumption from a link in the Grafana Dashboard.


## Table of Contents
- [Manual Installation](#manual-installation)
- [Dev Environment](#development-environment)
- [Project Structure](#project-structure)
- [Further Improvements](#further-improvements)


## Manual Installation

Clone the repo:

```bash
git clone https://github.com/michaelpappas/van_mqtt_client
cd van_mqtt_clint
```

Set the environment variables:
```bash
touch .env
# open .env and modify the environment variables
```
or
```bash
cp .env.example .env
# open .env and modify the environment variables
```
SECRET_KEY - Choose any string

DATABASE_URL - Replace the {postgres username} and {postgres password} with your personal postgres username and password.

More info regarding configuring postgres on a raspberry pi can be found [here](https://pimylifeup.com/raspberry-pi-postgresql/)

## Development Environment

In the cloned directory create a virtual environment
```bash
python3 -m venv venv
```

Activate that venv
```bash
source venv/bin/activate
```

Install the requirements
```
pip3 install -r requirements.txt
```

### Running the Script

Once all the requirements are installed and everything is configured you can start the MQTT client with
```bash
python3 mqttClient.py
```
and run the Flask server with
```bash
flask run -p (desired port)
```

Once all of this is working correctly it is suggested that you have both of these scripts begin on boot using cron.


## Project Structure

```
\                           # project directory
 |--.env.example            # example environment variables
 |--mqttClient.py           # main MQTT Client
 |--models.py               # models for battery and water tank data
 |--app.py                  # flask app for water consumption reset endpoint
 |--requirements.txt        # script requirements

```

## Further Improvements

1. Complete routing for MQTT messages in client to trigger correct response
2. Write test for flask endpoint, models,  and mqtt client
3. Code cleanup and refactor










