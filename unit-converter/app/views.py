from flask import Flask, render_template, request

from .measurements import (
    TEMPERATURE_UNITS,
    WEIGHT_UNITS,
    LENGTH_UNITS,
    convert_length,
    convert_temperature,
    convert_weight,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/length", methods=["GET", "POST"])
def length():
    result = value = from_unit = to_unit = error = None
    if request.method == "POST":
        try:
            value = float(request.form["value"])
            from_unit = request.form["from"]
            to_unit = request.form["to"]
            result = convert_length(value, from_unit, to_unit)
        except Exception as e:
            error = f"Error: {e}"
    return render_template(
        "length.html",
        units=LENGTH_UNITS,
        from_unit=from_unit,
        to_unit=to_unit,
        result=result,
        error=error,
    )


@app.route("/weight", methods=["GET", "POST"])
def weight():
    result = value = from_unit = to_unit = error = None
    if request.method == "POST":
        try:
            value = float(request.form["value"])
            from_unit = request.form["from"]
            to_unit = request.form["to"]
            result = convert_weight(value, from_unit, to_unit)
        except Exception as e:
            error = f"Error: {e}"
    return render_template(
        "weight.html",
        units=WEIGHT_UNITS,
        from_unit=from_unit,
        to_unit=to_unit,
        result=result,
        error=error,
    )


@app.route("/temperature", methods=["GET", "POST"])
def temperature():
    result = value = from_unit = to_unit = error = None
    if request.method == "POST":
        try:
            value = float(request.form["value"])
            from_unit = request.form["from"]
            to_unit = request.form["to"]
            result = convert_temperature(value, from_unit, to_unit)
        except Exception as e:
            error = f"Error: {e}"
    return render_template(
        "temperature.html",
        units=TEMPERATURE_UNITS,
        from_unit=from_unit,
        to_unit=to_unit,
        result=result,
        error=error,
    )
