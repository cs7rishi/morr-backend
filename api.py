from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS

# MongoDb Atlas having some network error so had to use local mongo Server
# uri = "mongodb+srv://cs7rishi:cs7hopa@morrcontactserver.6j9qt.mongodb.net/morr"
client = MongoClient('localhost', 27017, retryWrites=True)

morr = client.morr
contacts = morr.contacts

app = Flask(__name__)
cors = CORS(app)

CONTACTS_PER_PAGE = 10


def pagination(request):
    page = request.args.get('page', 1, type=int)
    start = (page-1)*CONTACTS_PER_PAGE

    limitContact = contacts.find({}).limit(CONTACTS_PER_PAGE).skip(start)

    return dumps(limitContact)


@app.route('/contact', methods=['GET'])
def retrieveContacts():

    current_contacts = pagination(request)

    if len(current_contacts) == 0:
        abort(404)
    return jsonify({
        "success": True,
        "contacts": current_contacts
    })


@app.route('/contact', methods=['POST'])
def addContact():
    body = request.get_json()

    id = body.get("id",None)
    name = body.get("name", None)
    mobile = body.get("mobile", None)

    try:
        insert_result = contacts.insert_one({"name": name, "mobile": mobile, "id" : id})

        return jsonify({
            'success':True,
            'acknowlegment':insert_result.acknowledged,
            'Id': insert_result.inserted_id
        })
    except:
        abort(422)


@app.route('/contact', methods=['PUT'])
def updateContactWithParticularId():
    body = request.get_json()
    id = body.get("id")
    name = body.get("name")

    try:
        update_result = contacts.update_one({"id": id}, {"$set": {"name": name}})
        
        return jsonify({
            'success':True,
            "acknowlegment":update_result.acknowledged
        })
    except:
        abort(404)


@app.route('/contact', methods=['DELETE'])
def deletewholeContactBook():
    body = request.get_json()
    id = body.get("id")

    try:
        deleted_result = contacts.delete_many({})

        return jsonify({
            "success": True,
            "acknowlegment":deleted_result.acknowledged
        })

    except:
        abort(422)

@app.route("/contact/<id>",methods=['DELETE'])
def deleteSingleContactByID(id):
    try:
        delete_result = contacts.delete_one({"id":id})
        return jsonify({
            "success" : True,
            "Acknowledgement": delete_result.acknowledged
        })
    except:
        abort(422)

@app.route('/contact/search',methods=['GET'])
def search():
    id = request.args.get("id")
    try:
        search_result = contacts.find_one({"id":id})

        return jsonify({
            "success":True,
            "contact": dumps(search_result,indent=2)
        })

    except:
        abort(204)



if __name__ == "__main__":

    app.run(debug=True, port=3000)
