DOMAIN = "climate"

SENSOR_ON = "on"
SENSOR_OFF = "off"

ATTR_HVAC_MODE = "hvac_mode"
ATTR_PRESET_MODE = "preset_mode"

SERVICE_TURN_OFF = "turn_off"
SERVICE_SET_HVAC_MODE = "set_hvac_mode"
SERVICE_SET_PRESET_MODE = "set_preset_mode"

ENTITY_ID = data.get("entity_id", None)
SENSORS_OFF = data.get("sensors_off", [])
SENSORS_WINDOWS = data.get("windows", [])
SENSOR_PRESENCE = data.get("sensor_presence", None)
HEATING_FROM_HOUR = data.get("heating_from_hour", None)
HEATING_TO_HOUR = data.get("heating_to_hour", None)

HVAC_OFF = "off"
PRESET_NONE = "none"
HVAC_ACTIVE = data.get("hvac_active", "heat")
PRESET_AWAY = data.get("preset_away", "Heat Eco")

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
for sensor_off in SENSORS_OFF:
    if hass.states.is_state(sensor_off, SENSOR_OFF):
        bool_off = True
for window in SENSORS_WINDOWS:
    # We invert this statement to catch 'None' as well
    if hass.states.is_state(window, SENSOR_ON):
        bool_off = True

# presence is true if not set or unavailable
bool_presence = (
    True
    if SENSOR_PRESENCE is None
    else not hass.states.is_state(SENSOR_PRESENCE, SENSOR_OFF)
)

state_climate = hass.states.get(ENTITY_ID)
current_state = state_climate.state
current_preset = state_climate.attributes.get(ATTR_PRESET_MODE, PRESET_NONE)

# set modes
if bool_off:
    # The heater should be off
    logger.info("Set %s to Off", ENTITY_ID)
    if current_state != HVAC_OFF:
        hass.services.call(DOMAIN, SERVICE_TURN_OFF, SERVICE_DATA, False)
    else:
        logger.info("The climate is already in the desired state")
else:
    # The heater should be on
    if bool_presence and (
        HEATING_FROM_HOUR is None
        or HEATING_TO_HOUR is None
        or is_time_between(
            datetime.time(hour=HEATING_FROM_HOUR), datetime.time(hour=HEATING_TO_HOUR),
        )
    ):
        # The heater should be in heating mode
        logger.info("Set %s to %s", ENTITY_ID, HVAC_ACTIVE)
        SERVICE_DATA[ATTR_HVAC_MODE] = HVAC_ACTIVE
        if current_state != HVAC_ACTIVE or current_preset != PRESET_NONE:
            hass.services.call(DOMAIN, SERVICE_SET_HVAC_MODE, SERVICE_DATA, False)
        else:
            logger.info("The climate is already in the desired state")
    else:
        # The heater should be in away mode
        logger.info("Set %s to %s", ENTITY_ID, PRESET_AWAY)
        SERVICE_DATA[ATTR_PRESET_MODE] = PRESET_AWAY
        if current_state != HVAC_ACTIVE or current_preset != PRESET_AWAY:
            hass.services.call(DOMAIN, SERVICE_SET_PRESET_MODE, SERVICE_DATA, False)
        else:
            logger.info("The climate is already in the desired state")
