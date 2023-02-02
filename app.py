import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Path to the sqlite db
database_path = "./Resources/hawaii.sqlite"

# create engine to hawaii.sqlite
engine = create_engine(f"sqlite:///{database_path}")


Base = automap_base()
Base.prepare(engine, reflect=True)


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
        f"All Available Routes:<br/>"
        f"Precipitation Route: /api/v1.0/precipitation<br/>"
        f"Observation Stations Route: /api/v1.0/stations<br/>"
        f"Most active station - Temperature Readings for one year Route: /api/v1.0/tobs<br/>"
        f"Temperature Readings from a selected date Route(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature Readings from start to end dates Route(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    
    #last_date
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date[0]
    latest_date=dt.datetime.strptime(recent_date,"%Y-%m-%d")
    last_date=latest_date-dt.timedelta(days=365)

    #results
    results = session.query(Measurement.date,func.avg(Measurement.prcp)).\
      filter(Measurement.date < latest_date).\
      filter(Measurement.date > last_date).\
        order_by(Measurement.date).\
        group_by(Measurement.date).\
        all()

    session.close()

    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        
        stations.append(station_dict)
  

    return jsonify(stations)


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    #last_date
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date[0]
    latest_date=dt.datetime.strptime(recent_date,"%Y-%m-%d")
    last_date=latest_date-dt.timedelta(days=365)

    #results
    # Query all date and tobs values
    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last_date).\
        filter(Measurement.station == 'USC00519281').all()

    session.close()

    tobs_data = []
    for date, tobs in results:
            tobs_dict = {}
            tobs_dict[date] = tobs
            tobs_data.append(tobs_dict)
    

    return jsonify(tobs_data)
   


@app.route('/api/v1.0/<start>')
def findall_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    all_tobs = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)



@app.route('/api/v1.0/<start>/<stop>')
def findall_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    all_tobs = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

if __name__ == '__main__':
    app.run(debug=True)