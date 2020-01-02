# Climate Analysis
# Lyna Olivares

import numpy as np
import os
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table

Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"       
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/argument: yyyy-mm-dd<br/>"
        f"/api/v1.0/date_range/argument: yyyy-mm-dd, yyyy-mm-dd<br/>"
    )


@app.route("/api/v1.0/percipitation")
def percipitation():
    """Return a list of all Percipitation Infromation"""
    #return (f"Last avaliable year of Percipitation Data for Hawaii:<br/>" )

    # Query all passengers
    session = Session(engine)
    
    results = session.query(Measurement.prcp).all()

    # close the session to end the communication with the database
    session.close()

    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)


@app.route("/api/v1.0/stations")
def station_name():
    """Return a list of passenger data including the name, age, and sex of each passenger"""

    # Open a communication session with the database
    session = Session(engine)

    # Query all passengers
    results = session.query(Station.station).all()

    # close the session to end the communication with the database
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    
    all_results = list(np.ravel(results))

    return jsonify(all_results)

@app.route("/api/v1.0/tobs")
def observations():
    """Return a list of all Observation for last Year Infromation"""
    #return (f"Last avaliable year of Percipitation Data for Hawaii:<br/>" )

    # Query all passengers
    session = Session(engine)
    
    maxdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for d in maxdate:
        yyyy = int(d[0:4])
        mm = int(d[5:7])
        dd = int(d[8:10])

    query_date = str(dt.date(yyyy, mm, dd) - dt.timedelta(days=365))
    
    results = session.query(Measurement.date,
                            Measurement.station,
                            Measurement.tobs).filter(Measurement.date >= query_date).all()

    # close the session to end the communication with the database
    session.close()

    # Convert list of tuples into normal list

    all_tobs = []
    for obvs in results:
        obvs_dict = {}
        obvs_dict["date"] = obvs.date
        obvs_dict["station"] = obvs.station
        obvs_dict["tobs"] = obvs.tobs
        all_tobs.append(obvs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/start_date/<start_date>")
def obvs_by_date(start_date):
    """Fetch the temperature observations >= start date, or a 404 if not."""
    
    session = Session(engine)

    min_rslt = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    max_rslt = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    avg_rslt = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    
    session.close()
    
    obvs_dict = {
        "min_observations": min_rslt, 
        "max_observations": max_rslt, 
        "avg_observations": avg_rslt
    }

    return jsonify(obvs_dict)

    return jsonify({"error": f"Date not in Data Set or format incorrect, yyyy-mm-dd."}), 404


@app.route("/api/v1.0/date_range/<startd>, <endd>")
def obvs_date_range(startd, endd):
    """Fetch the temperature observations for date range, or a 404 if not."""
    
    session = Session(engine)

    min_rslt = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= startd).filter(Measurement.date <= endd).all()
    max_rslt = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= startd).filter(Measurement.date <= endd).all()
    avg_rslt = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= startd).filter(Measurement.date <= endd).all()
    
   
    session.close()
    
    obvs_dict = {
        "min_observations": min_rslt, 
        "max_observations": max_rslt, 
        "avg_observations": avg_rslt
    }

    return jsonify(obvs_dict)

    return jsonify({"error": f"Date not in Data Set or format incorrect, yyyy-mm-dd."}), 404

if __name__ == '__main__':
    app.run(debug=True)
