import csv
import requests
import json
from optparse import OptionParser


REGISTER_URL = 'http://127.0.0.1:5000/register'

def main():
    options, args = parse_arguments()
    print(options.input)
    read_file(options.input)


def parse_arguments():
    """
    Gets the path where to find the .vcf file from gnomAD from command line with -i, --input

    :return .parse_args(): Dictionary with values passed from command line
    """
    parser = OptionParser(description="Fills the DB by http post request")
    parser.add_option("-i", "--input", help="path to .vcf file")
    
    return parser.parse_args()


def read_file(filepath):
    """
    Reads the .vcf file from gnomAD and checks if each variant has an AF(allele frequency) of >1% and if
    not all of not all of the allele counts is from the non_cancer subset

    :param filepath: path to the .vcf file
    """
    try:
        with open(filepath) as file:
            reader = csv.reader(file, delimiter = "\t")
            for row in reader:
                if row[0][:1] != "#":
                    info = row[7].split(";")
                    info_dict = {}
                    for i in info:
                        if "=" in i:
                            split = i.split("=")
                            info_dict[split[0]] = split[1]
                    
                    if "AF" in info_dict:
                        af = float(info_dict["AF"])
                    if "non_cancer_AF" in info_dict:
                        nc_af = float(info_dict["non_cancer_AF"])
                    
                    if(af < 0.01 and nc_af < af):
                        post_req(row[2], int(row[0]), int(row[1]), row[3], row[4], af, nc_af)
    except IndexError:
        print(row)

def post_req(ID, chromosome, position, reference, alternate, af, nc_af):
    """
    Fill the mongoDB with a variant by HTTP post request.
    
    :param ID: variant id(ex. rs145331222)
    :param chromosome: chromosome of variant
    :param position: position of variant
    :param reference: reference nucleotide(s)
    :param alternate: alternate nucleotide(s)
    :param af: allele frequency of variant
    :param nc_af: allele frequence of variant in non_cancer subset
    """
    variant_dict = {
        "ID": ID,
        "Chromosome": chromosome,
        "Position": position,
        "Reference": reference,
        "Alternate": alternate,
        "Allele_frequency": af,
        "NC_frequency": nc_af
    }
    variant_json = json.dumps(variant_dict)

    requests.post(REGISTER_URL, json = variant_json)


if __name__ == "__main__":
    main()


