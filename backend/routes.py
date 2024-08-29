from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    """Return all picture URLs in JSON format"""
    if data:
        return jsonify(data), 200
    return jsonify({"message": "No data found"}), 404

######################################################################
# GET A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    """Return the picture URL for the given id"""
    try:
        # Search for the picture with the given id
        picture = next((item for item in data if item.get("id") == id), None)
        
        if picture:
            return jsonify(picture), 200  # Return the picture if found
        else:
            return jsonify({"message": "Picture not found"}), 404  # Return 404 if not found
    except Exception as e:
        return jsonify({"error": str(e)}), 500

######################################################################
# CREATE A PICTURE
######################################################################
@app.route("/picture", methods=["POST"])
def create_picture():

    # get data from the json body
    picture_in = request.json
    print(picture_in)

    # if the id is already there, return 303 with the URL for the resource
    for picture in data:
        if picture_in["id"] == picture["id"]:
            return {
                "Message": f"picture with id {picture_in['id']} already present"
            }, 302

    data.append(picture_in)
    return picture_in, 201

######################################################################
# UPDATE A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    """Update an existing picture entry"""
    try:
        # Extract the updated picture data from the request body
        updated_picture = request.get_json()
        
        # Define required fields
        required_fields = ["id", "pic_url", "event_country", "event_state", "event_city", "event_date"]
        
        # Check if all required fields are present
        if not all(field in updated_picture for field in required_fields):
            return jsonify({"Message": "Missing required fields"}), 400

        # Find the existing picture with the given id
        picture_index = next((index for (index, item) in enumerate(data) if item.get("id") == id), None)
        
        if picture_index is not None:
            # Update the existing picture
            data[picture_index] = updated_picture
            
            # Save the updated data to the JSON file
            with open(json_url, "w") as file:
                json.dump(data, file, indent=4)

            return jsonify(updated_picture), 200

        else:
            # Picture with the given id does not exist
            return jsonify({"message": "picture not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

######################################################################
# DELETE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):

    for picture in data:
        if picture["id"] == id:
            data.remove(picture)
            return "", 204

    return {"message": "picture not found"}, 404
