DOMAIN = "climate"
ENTITY_ID = data.get("entity_id", None)
SENSORS_OFF = data.get("sensors_off", [])
SENSORS_WINDOWS = data.get("windows", [])
SENSOR_PRESENCE = data.get("sensor_presence", None)
HEATING_FROM_HOUR = data.get("heating_from_hour", None)
HEATING_TO_HOUR = data.get("heating_to_hour", None)
ACTIVE_MODE = data.get("active_mode", "heat")
AWAY_PRESET = data.get("away_preset", "Heat Eco")
NONE_PRESET = "None"
OFF_MODE = "off"
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
    if hass.states.is_state(sensor_off, "off"):
        bool_off = True
for window in SENSORS_WINDOWS:
    # We invert this statement to catch 'None' as well
    if hass.states.is_state(window, "on"):
        bool_off = True

# presence is true if not set or unavailable
bool_presence = (
    True
    if SENSOR_PRESENCE is None
    else not hass.states.is_state(SENSOR_PRESENCE, "off")
)

state_climate = hass.states.get(ENTITY_ID)

# set modes
if bool_off:
    # The heater should be off
    logger.info("Set %s to Off", ENTITY_ID)
    if state_climate.state != OFF_MODE:
        hass.services.call(DOMAIN, "turn_off", SERVICE_DATA, False)
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
        logger.info("Set %s to %s", ENTITY_ID, ACTIVE_MODE)
        SERVICE_DATA["hvac_mode"] = ACTIVE_MODE
        if (
            state_climate.state != ACTIVE_MODE
            or state_climate.preset_mode != NONE_PRESET
        ):
            hass.services.call(DOMAIN, "set_hvac_mode", SERVICE_DATA, False)
        else:
            logger.info("The climate is already in the desired state")
    else:
        # The heater should be in away mode
        logger.info("Set %s to %s", ENTITY_ID, AWAY_PRESET)
        SERVICE_DATA["preset_mode"] = AWAY_PRESET
        if (
            state_climate.state != ACTIVE_MODE
            or state_climate.preset_mode != AWAY_PRESET
        ):
            hass.services.call(DOMAIN, "set_preset_mode", SERVICE_DATA, False)
        else:
            logger.info("The climate is already in the desired state")
