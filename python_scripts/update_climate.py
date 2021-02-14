DOMAIN = "climate"

STATE_ON = "on"
STATE_OFF = "off"
STATE_HEAT = "heat"

ATTR_TEMPERATURE = "temperature"
ATTR_HVAC_MODE = "hvac_mode"
SERVICE_TURN_OFF = "turn_off"
SERVICE_TURN_ON = "turn_on"
SERVICE_SET_TEMP = "set_temperature"

ENTITY_ID = data.get("entity_id", None)
SENSOR_OFF = data.get("sensor_off", None)
SENSOR_ON = data.get("sensor_on", None)
SENSOR_PRESENCE = data.get("sensor_presence", None)
HEATING_FROM_HOUR = int(data.get("heating_from_hour", -1))
HEATING_TO_HOUR = int(data.get("heating_to_hour", -1))
HIGH_TEMP = int(data.get("high_temp", 25))
LOW_TEMP = int(data.get("low_temp", 20))

SERVICE_DATA = {"entity_id": ENTITY_ID}


def is_time_between(begin_time, end_time) -> bool:
    check_time = dt_util.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


# validate input
if not ENTITY_ID:
    logger.error("You have to set an entity_id")

# extract states
bool_off = False
if hass.states.is_state(SENSOR_OFF, STATE_ON):
    logger.debug(f"SENSOR_OFF: {hass.states.get(SENSOR_OFF).state}")
    bool_off = True
if hass.states.is_state(SENSOR_ON, STATE_OFF):
    logger.debug(f"SENSOR_ON: {hass.states.get(SENSOR_ON).state}")
    bool_off = True

# presence is true if not set or unavailable
bool_presence = (
    True
    if SENSOR_PRESENCE is None
    else not hass.states.is_state(SENSOR_PRESENCE, STATE_OFF)
)
logger.debug(f"bool presence is {bool_presence}")

state_climate = hass.states.get(ENTITY_ID)
current_state = state_climate.state
current_temp = state_climate.attributes.get(ATTR_TEMPERATURE, 0)

# set modes
if bool_off:
    # The heater should be off
    logger.info("Turn %s off", ENTITY_ID)
    if current_state != STATE_OFF:
        hass.services.call(DOMAIN, SERVICE_TURN_OFF, SERVICE_DATA, False)
    else:
        logger.info("The climate is already off")
else:
    # The heater should be on
    logger.info("Turn %s on", ENTITY_ID)
    if current_state == STATE_OFF:
        hass.services.call(DOMAIN, SERVICE_TURN_ON, SERVICE_DATA, False)
    else:
        logger.info("The climate is already on")

    if bool_presence and (
        HEATING_FROM_HOUR == -1
        or HEATING_TO_HOUR == -1
        or is_time_between(
            datetime.time(hour=HEATING_FROM_HOUR),
            datetime.time(hour=HEATING_TO_HOUR),
        )
    ):
        # The heater should be in heating mode
        logger.info("Set %s to %s", ENTITY_ID, HIGH_TEMP)
        SERVICE_DATA[ATTR_TEMPERATURE] = HIGH_TEMP
        SERVICE_DATA[ATTR_HVAC_MODE] = STATE_HEAT
        if current_state != STATE_HEAT or current_temp != HIGH_TEMP:
            hass.services.call(DOMAIN, SERVICE_SET_TEMP, SERVICE_DATA, False)
        else:
            logger.info("The climate is already in the desired state")
    else:
        # The heater should be in away mode
        logger.info("Set %s to %s", ENTITY_ID, LOW_TEMP)
        SERVICE_DATA[ATTR_TEMPERATURE] = LOW_TEMP
        SERVICE_DATA[ATTR_HVAC_MODE] = STATE_HEAT
        if current_state != STATE_HEAT or current_temp != LOW_TEMP:
            hass.services.call(DOMAIN, SERVICE_SET_TEMP, SERVICE_DATA, False)
        else:
            logger.info("The climate is already in the desired state")
