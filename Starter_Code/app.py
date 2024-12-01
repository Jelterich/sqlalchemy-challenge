# Import the dependencies.
import datetime as dt  # For date manipulation
import numpy as np  # For numerical operations (e.g., flattening query results)
from sqlalchemy.ext.automap import automap_base  # For ORM mapping
from sqlalchemy.orm import Session  # For database session management
from sqlalchemy import create_engine, func  # For engine creation and SQL functions
from flask import Flask, jsonify  # For Flask application and JSON output


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Define the home route ("/") for the API
@app.route("/")
def welcome():
    """
    Home route for the Hawaii Climate Analysis API.
    Lists all available API routes.
    """
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Last 12 months of precipitation data<br/>"
        f"/api/v1.0/stations - List of all weather stations<br/>"
        f"/api/v1.0/tobs - Last 12 months of temperature observations for the most active station<br/>"
        f"/api/v1.0/temp/<start> - Temperature stats from the start date<br/>"
        f"/api/v1.0/temp/<start>/<end> - Temperature stats for a date range<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
    session = Session(engine)

    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    precipitation_data = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    session.close()

    # Convert results to a dictionary and return as JSON
    precip_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all weather stations."""
    session = Session(engine)

    # Query all station IDs
    stations_data = session.query(Station.station).all()
    session.close()

    # Convert results to a list
    stations_list = [station[0] for station in stations_data]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the last year for the most active station."""
    session = Session(engine)

    # Identify the most active station
    most_active_station = (
        session.query(Measurement.station, func.count(Measurement.station))
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )

    # Query temperature observations for the last 12 months
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    tobs_data = (
        session.query(Measurement.tobs)
        .filter(Measurement.station == most_active_station)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    session.close()

    # Convert results to a list
    temperatures = [temp[0] for temp in tobs_data]
    return jsonify(temperatures)

@app.route("/api/v1.0/temp/<start>")
def temp_stats_start(start):
    """Return temperature stats (min, avg, max) from a start date."""
    session = Session(engine)

    # Query temperature stats
    stats = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start)
        .all()
    )
    session.close()

    return jsonify(stats[0])

@app.route("/api/v1.0/temp/<start>/<end>")
def temp_stats_range(start, end):
    """Return temperature stats (min, avg, max) for a date range."""
    session = Session(engine)

    # Query temperature stats for the date range
    stats = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )
    session.close()

    return jsonify(stats[0])

if __name__ == "__main__":
    app.run(debug=True)
