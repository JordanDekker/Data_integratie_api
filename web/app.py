from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://my_db:27017")
db = client.variantDB
var_coll = db["variants"]
saved_coll = db["savedResults"]


class Variant(Resource):
    def get(self, id):
        
        output = []
        for variant in var_coll.find({"ID": id}):
            output.append({'ID': variant['ID'], 'Chromosome': variant['Chromosome'], 'Position': variant['Position'], 'Reference': variant['Reference'],
                    'Alternate': variant['Alternate'], 'Allele_frequency': variant['Allele_frequency'], 'Cancer_allele_frequency': variant['NC_frequency']})

        return jsonify({"result": output})


class List(Resource):
    def get(self):

        output = []
        for x in var_coll.find():
            output.append({"id": x["ID"], "chromosome": x["Chromosome"], "position": x["Position"], "reference": x["Reference"],
                            "alternate": x["Alternate"], "af": x["Allele_frequency"], "nc_af": x["NC_frequency"]})
        return jsonify({"result": output})


class Query(Resource):
    def get(self):

        chromosome = request.args.get('chromosome')
        position = request.args.get('position', type=check_if_range)
        reference = request.args.get('reference')
        alternate = request.args.get('alternate')

        if isinstance(position, list): 
            query = {"$and": [
                {"Chromosome": int(chromosome)},
                {"Position": {"$gte": position[0], "$lte": position[1]}},
                {"Reference": reference},
                {"Alternate": alternate}
            ]}
        else:
            query = {"$and": [
                {"Chromosome": int(chromosome)},
                {"Position": position},
                {"Reference": reference},
                {"Alternate": alternate}
            ]}


        output = []
        for x in var_coll.find(query):
            output.append({"id": x["ID"], "chromosome": x["Chromosome"], "position": x["Position"], "reference": x["Reference"],
                            "alternate": x["Alternate"], "af": x["Allele_frequency"], "nc_af": x["NC_frequency"]})
        
        return jsonify({"result": output})


class SaveResult(Resource):
    def post(self):

        try:
            s = request.get_json()
            data = eval(s)

            rs_ids = data["rsIDs"]

            alternate = data["rsIDs"][1]

            __id = saved_coll.insert_one({
                "savedIDs": rs_ids,
            })

            objectID = str(__id.inserted_id)

            retJson = {
                "status": 200,
                "objectid": objectID
            }
            return jsonify(retJson)
        except:
            return jsonify({
                "status": 400,
                "message": "failed to save file"
            })


class GetSavedResult(Resource):
    def get(self, id):

        rs_ids = saved_coll.find_one({'_id': ObjectId(id) })["savedIDs"]

        output = []
        for i in rs_ids:
            x = var_coll.find_one({'ID':i[0], "Alternate":i[1]})
            output.append({"id": x["ID"], "chromosome": x["Chromosome"], "position": x["Position"], "reference": x["Reference"],
                            "alternate": x["Alternate"], "af": x["Allele_frequency"], "nc_af": x["NC_frequency"]})
                
        return jsonify({"result": output})  


class Register(Resource):
    def post(self):

        s = request.get_json()
        data=eval(s)

        ID = data["ID"]
        chromosome = data["Chromosome"]
        position = data["Position"]
        reference = data["Reference"]
        alternate = data["Alternate"]
        af = data["Allele_frequency"]
        nc_af = data["NC_frequency"]


        var_coll.insert({
            "ID": ID,
            "Chromosome": chromosome,
            "Position": position,
            "Reference": reference,
            "Alternate": alternate,
            "Allele_frequency": af,
            "NC_frequency": nc_af
        })

        retJson = {
            "status": 200,
            "msg": "Registration Succesful"
        }
        return jsonify(retJson)


def check_if_range(position):
    """
    Checks if given position parameter is single or range

    :param position: either a single position or a range position (500-600)

    :return: single position as integer or 2 integers as list
    """
    if '-' in position:
        return list(map(int, position.split('-')))
    
    return int(position)


def variantExist(chromosome, position, reference, alternate):
    """
    Checks if variant exists in mongoDB

    :param chromosome: given chromosome
    :param position: given position
    :param reference: given reference
    :param alternate: given alternate

    :return boolean:
    """
    if var_coll.find({"$and": [
            {"Chromosome": int(chromosome)},
            {"Position": int(position)},
            {"Reference": reference},
            {"Alternate": alternate}
        ]}).count() == 0:
        return False
    else:
        return True


api.add_resource(Variant, '/variant/<id>')
api.add_resource(List, '/list')
api.add_resource(Query, '/query')
api.add_resource(SaveResult, '/save')
api.add_resource(GetSavedResult, '/id/<id>')
api.add_resource(Register, '/register')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)