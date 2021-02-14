# HA-UpdateClimate

[![hacs](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat)](https://github.com/custom-components/hacs)
[![license](https://img.shields.io/github/license/Santobert/HA-UpdateClimate.svg?style=flat)](https://github.com/Santobert/HA-UpdateClimate/blob/master/LICENSE)
[![release](https://img.shields.io/github/v/release/Santobert/HA-UpdateClimate.svg?style=flat)](https://github.com/Santobert/HA-UpdateClimate/releases)
[![last-commit](https://img.shields.io/github/last-commit/Santobert/HA-UpdateClimate.svg?style=flat)](https://github.com/Santobert/HA-UpdateClimate/commits/master)
[![language](https://img.shields.io/github/languages/top/Santobert/HA-UpdateClimate.svg?style=flat)](https://github.com/Santobert/HA-UpdateClimate)
[![code-size](https://img.shields.io/github/languages/code-size/Santobert/HA-UpdateClimate.svg?style=flat)](https://github.com/Santobert/HA-UpdateClimate)

Python script to update climate devices based on sensors and time.

## Installation

Install via HACS (recommended) or download the `update_climate.py` file from inside the python_scripts directory here to your local python_scripts directory, then reload python_scripts in Home Assistant.

There is a blueprint that simplifies the use of this script:
<https://github.com/Santobert/HA-UpdateClimate/blob/master/blueprints/update_climate.yaml>

## Usage

This python script sets the target temperature according to the specified sensors and time.

![BPMN](bpmn.png)

The climate entity will be _off_ when:

- The given `sensors_on` is _on_
- The given `sensors_off` is _off_

In all other cases the `hvac_mode` will be `heat`.
The target temparature will be set to `high_temp` if the `sensor_presence` is _on_ or not given and the current time is between `heating_from_hour` and `heating_to_hour`.
Otherwise the target temperature will be set to `low_temp`.
If one of the specifications `heating_from_hour` or `heating_to_hour` is not given, the target temperature depends only on the `sensor_presence`.

| Name              | Required | Description                                                 |
| ----------------- | -------- | ----------------------------------------------------------- |
| entity_id         | True     | The climates enitity_id                                     |
| sensor_on         | False    | The climate will be off when this sensors is on             |
| sensor_off        | False    | The climate will be off when this sensors is off            |
| sensor_presence   | False    | The climate will switch to active mode if this sensor is on |
| heating_from_hour | False    | Start time from which heating is to start                   |
| heating_to_hour   | False    | End time to which the heating is to last                    |
| high_temp         | False    | Temperature for active hours (Default: 25)                  |
| low_temp          | False    | Temperature for inactive hours (Default: 20)                |

## Service Example

The following is the content of a [service call](https://www.home-assistant.io/docs/scripts/service-calls/).
This example includes all possible parameters.
You may not need them all.

```yaml
service: python_script.update_climate
data:
  entity_id: climate.livingroom
  sensor_on: binary_sensor.livingroom_window
  sensor_off: binary_sensor.livingroom_climate_on
  sensor_presence: binary_sensor.someone_at_home
  heating_from_hour: 8
  heating_to_hour: 17
  high_temp: 25
  low_temp: 20
```

## Automation example

The following is the content of an [automation](https://www.home-assistant.io/docs/automation/).
This works with Eurotronic Spirit Z-Wave thermostats.
To use different devices, you may want to change `hvac_active` and `preset_away`.

```yaml
- id: 0123456789
  alias: Climate Livingroom
  trigger:
    - hours: "*"
      minutes: "1"
      platform: time_pattern
    - entity_id: binary_sensor.presence
      platform: state
    - entity_id: binary_sensor.livingroom_window
      platform: state
    - entity_id: input_boolean.livingroom_climate
      platform: state
    - entity_id: binary_sensor.all_climates_on
      platform: state
  condition: []
  action:
    - data:
        entity_id: climate.livingroom
        sensor_on: binary_sensor.livingroom_window
        sensor_off: binary_sensor.livingroom_climate_on
        sensor_presence: binary_sensor.someone_at_home
        heating_from_hour: 8
        heating_to_hour: 17
        high_temp: 25
        low_temp: 20
      service: python_script.update_climate
```
