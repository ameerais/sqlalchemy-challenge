# Import dependencies
import numpy as np
import pandas as pd
from flask import Flask, jsonify

# Import SQLAlchemy dependencies
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Set up database
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Initialize Flask application
app = Flask(__name__)

# Define routes
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year."""
    session = Session(engine)
    # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= "2016-08-23").all()
    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    session = Session(engine)
    # Query all stations
    results = session.query(Station.station).all()
    session.close()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations (TOBS) for the previous year."""
    session = Session(engine)
    # Query the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(
        func.count(Measurement.station).desc()).first()[0]

    # Query the last 12 months of temperature observation data for this station
    results = session.query(Measurement.tobs).filter(
        Measurement.station == most_active_station).filter(
        Measurement.date >= "2016-08-23").all()
    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX for a given date range."""
    session = Session(engine)

    # Select statement for min, avg, and max temps
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # Calculate TMIN, TAVG, TMAX for all dates greater than or equal to start
        results = session.query(*sel).filter(Measurement.date >= start).all()
    else:
        # Calculate TMIN, TAVG, TMAX for dates between the start and end date inclusive
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
