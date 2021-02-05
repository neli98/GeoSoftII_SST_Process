from flask import Flask, request, jsonify,Response
import requests
import os
import mean_sst
import threading
import xarray
import json
import uuid
docker = False
app = Flask(__name__)




job = {"status": None, "id": None, "jobid": None, "errorType":None}

@app.route("/doJob/<uuid:id>", methods=["POST"])
def doJob(id):
    dataFromPost = request.get_json()
    job["status"] = "processing"
    t = threading.Thread(target=jobwrapper, args=(dataFromPost, id,))
    t.start()
    return Response(status=200)

@app.route("/jobStatus", methods=["GET"])
def jobStatus():
    return jsonify(job)

def jobwrapper(dataFromPost, id):
    Job(dataFromPost, id)
    try:
        #Job(dataFromPost, id)
        print("Test")
    except:
        job["status"] = "error"
        job["errorType"] = "Unkown Error"
        return

#zum testen: requests.post("localhost:80/doJob",json={"arguments":{"data":data,"timeframe":["1984-10-01","1984-11-01"],"bbox":[-999,-999,-999,-999]}})


def Job(dataFromPost, id):
    job["status"] = "running"
    job["jobid"] = str(id)
    #Funktionsaufruf von wrapper_mean_sst
    dataset = xarray.open_dataset("data/" + str(id) +"/"+ str(dataFromPost["arguments"]["data"]["from_node"])+".nc")
    x = mean_sst.wrapper_mean_sst(data=dataset, timeframe=dataFromPost["arguments"]["timeframe"],
                                  bbox=dataFromPost["arguments"]["bbox"])

    try:
        #x = mean_sst.wrapper_mean_sst(data=dataset,timeframe=dataFromPost["arguments"]["timeframe"],bbox=dataFromPost["arguments"]["bbox"])
        print("Test")

    except mean_sst.ParameterTypeError as e: #Datentypen von Bbox oder Timeframe stimmen nicht
        job["status"] = "error"
        job["errorType"] ="ParameterTypeError"
        return
    except mean_sst.BboxLengthError as e: #Bbox hat nicht 4 Elemente
        job["status"] = "error"
        job["errorType"] = "BboxLengthError"
        return
    except mean_sst.LongitudeValueError as e: #Bbox Out of bounds
        job["status"] = "error"
        job["errorType"] = "LongitudeValueError"
        return
    except mean_sst.LatitudeValueError as e: #Bbox Out of bounds
        job["status"] = "error"
        job["errorType"] = "LatitudeValueError"
        return
    except mean_sst.BboxCellsizeError as e: #Bbox abstand zu klein
        job["status"] = "error"
        job["errorType"] = "BboxCellsizeError"
        return
    except mean_sst.TimeframeLengthError as e: #Timeframe keine 2 elemente
        job["status"] = "error"
        job["errorType"] = "TimeframeLengthError"
        return
    except mean_sst.TimeframeValueError as e: #Timeframe out of bound
        job["status"] = "error"
        job["errorType"] = "TimeframeValueError"
        return
    except:
        job["status"] = "error"
        job["errorType"] = "UnkownError"
        return


    subid = uuid.uuid1()
    x.to_netcdf("data/"+str(id)+"/"+str(subid)+".nc")
    job["id"] = str(subid)
    job["status"]="done"






def main():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    global docker
    if os.environ.get("DOCKER") == "True":
        docker = True
    if docker:
        port = 80
    else:
        port=442
    app.run(debug=True, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()