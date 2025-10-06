"""Measurement"""

from collections import namedtuple


Unit = namedtuple("Unit", ["name", "factor"], defaults=[None])

LENGTH_UNITS = {
    "mm": Unit("millimeter", 0.001),
    "cm": Unit("centimeter", 0.01),
    "dm": Unit("decimeter", 0.1),
    "m": Unit("meter", 1),
    "km": Unit("kilometer", 1000),
    "in": Unit("inch", 0.0254),
    "ft": Unit("foot", 0.3048),
    "yd": Unit("yard", 0.9144),
    "mi": Unit("mile", 1609.344),
}

WEIGHT_UNITS = {
    "mg": Unit("milligram", 0.001),
    "g": Unit("gram", 1),
    "kg": Unit("kilogram", 1000),
    "t": Unit("ton", 1000000),
    "oz": Unit("ounce", 28.349523125),
    "lb": Unit("pound", 453.59237),
}

TEMPERATURE_UNITS = {
    "C": Unit("Celsius"),
    "F": Unit("Fahrenheit"),
    "K": Unit("Kelvin"),
}


def convert_length(value: float, from_unit: str, to_unit: str) -> float:
    return round(value * LENGTH_UNITS[from_unit].factor / LENGTH_UNITS[to_unit].factor, 12)


def convert_weight(value: float, from_unit: str, to_unit: str) -> float:
    return round(value * WEIGHT_UNITS[from_unit].factor / WEIGHT_UNITS[to_unit].factor, 12)


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    # Convert from from_unit to Celsius
    if from_unit == to_unit:
        return value
    if from_unit == "C":
        celsius = value
    elif from_unit == "F":
        celsius = (value - 32) * 5 / 9
    else:
        celsius = value - 273.15
    # Convert from Celsius to to_unit
    if to_unit == "C":
        result = celsius
    elif to_unit == "F":
        result = celsius * 9 / 5 + 32
    else:
        result = celsius + 273.15
    return round(result, 2)
