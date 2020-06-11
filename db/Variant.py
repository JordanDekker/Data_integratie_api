from mongoengine import *

from datetime import datetime
import os
import json

# connect("variantDB")

# Defining documents

class Variant(Document):
    ID = StringField(required=True)
    chromosome = IntField(required=True)
    position = IntField(required=True)
    reference = StringField()
    alternate = StringField()
    af = FloatField()
    nc_af = FloatField()

    def json(self):
        variant_dict = {
            "ID": self.ID,
            "chromosome": self.chromosome,
            "position": self.position,
            "reference": self.reference,
            "alternate": self.alternate,
            "af": self.af,
            "nc_af": self.nc_af
        }
        return json.dumps(variant_dict)

    
    meta = {
        "indexes": [
            {'fields': ("ID", "position","reference", "alternate"), 'unique': True}],
        "ordering": ["-af"]
        
    }


