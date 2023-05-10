@app.route("/compleete_bed", methods=['POST'])
def compleete_bed():
    try:
        data = request.get_json()
        if data:
                #create id
            upload_id = uuid.uuid4().hex
            #gather data
            value1 = data.get("value1")
            value2 = data.get("value2")
            value3 = data.get("value3")

            upload_data = {
            'upload_id': upload_id,
            'value1': value1,
            'value2': value2,
            'value3': value3, 
            }

            #add plantbed
            SENSOR.document(upload_id).set(data)
            
            return response, 200
        else:
            response = "No plantbed provided.", 400
        return response
    except Exception as e:
        return str(e), 400