from web import app
import csv
import json
import requests
from optparse import OptionParser
from pymongo import MongoClient
import urllib.request

QUERY_URL = 'http://127.0.0.1:5000/query'
SAVE_URL = 'http://127.0.0.1:5000/save'


def main():
    options, args = parse_arguments()
    variant_hits = read_file(options.input)
    print(options)
    if options.output:
        save_to_file(options.output, variant_hits)
    if  options.save:
        object_id = save_to_mongoDB(variant_hits)
        print(object_id)


def parse_arguments():
    """
    Gets options from the command line

    :return .parse_args(): Dictionary with values passed from command line
    """
    parser = OptionParser(description="Checks if variants from input file exists in DB")
    parser.add_option("-i", "--input", help="path to .vcf file")
    parser.add_option("-o", "--output", help="write report to filepath", default="output.json")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False, help="don't print json to stdout")
    parser.add_option("-s", "--save", action="store_true", dest="save", default=False, help="saves output variants in mongoDB")

    return parser.parse_args()


def read_file(filepath):
    """
    Loops through the given .vcf file and calls get_variant() if the variant is found in the mongoDB

    :param filepath: path to the given .vcf file which will be queried to the mongoDB

    :return variant_hits:  a list with dictionaries for each variant which has been found in the mongoDB
    """
    variant_hits = []

    try:
        with open(filepath) as file:
            reader = csv.reader(file, delimiter = "\t")
            for row in reader:
                if row[0][:1] != "#":
                    data = get_variant(row[0], row[1], row[3], row[4])
                    if data:
                        variant_hits.append(data)
    except FileNotFoundError as fnfe:
        print(fnfe)

    return variant_hits



def get_variant(chromosome, position, reference, alternate):
    """
    Performs a HTTP get request to find if variant is in the mongoDB
    
    :param chromosome: chromosome of variant
    :param position: position of variant
    :param reference: reference nucleotide(s) of variant
    :param alternate: alternate nucleotide(s) of variant

    :return data['result']: A dictionary with information about the variant, only returns it when found in mongoDB
    
    """
    params = {"chromosome": int(chromosome),
            "position": int(position),
            "reference": reference,
            "alternate": alternate}
    r = requests.get(url = QUERY_URL, params = params)
    data = r.json()
    if data['result']:
        return data['result']


def save_to_file(filepath, variant_hits):
    """
    Saves the variants which are a found in the mongoDB to a given file

    :param filepath: path where to save the resulting variants
    :param variant_hits: a list with dictionaries for each variant which has been found in the mongoDB
    """

    with open(filepath, 'w') as fout:
        json.dump(variant_hits , fout)
    

def save_to_mongoDB(variant_hits):
    """
    Saves the found variants in the db.savedResults collection in the mongoDB.
    This is for easy access to saved files

    :param variant_hits: a list with dictionaries for each variant which has been found in the mongoDB

    :return object_id: the objectid created by mongodb
    """
    rsIds_list = []

    for x in variant_hits:
        print(x)
        rsIds_list.append([x[0]["id"], x[0]["alternate"]])

    myobj = {
        "rsIDs": rsIds_list,
    }
    data_json = json.dumps(myobj)

    post = requests.post(SAVE_URL, json = data_json)
    object_id = eval(post.text)["objectid"]

    return object_id


if __name__ == "__main__":
    main()