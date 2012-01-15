#!/usr/bin/env python
import math
import util
import distance

class House(object):
    REQUIRED = ['MLS', 'Price', 'Address', 'HOA', 'Taxes']
    def __init__(self, **kwargs):
        for r in House.REQUIRED:
            if r not in kwargs.keys():
                raise ValueError('{0} must be specified'.format(r))
        for k,v in kwargs.iteritems():
            setattr(self, k, v)
        self.distances = {}
    def distance_to(self, locname, addr):
        # Store the distance
        self.distances[locname.lower()] = distance.calculate_distance(self.Address, addr)
        return self.distances[locname.lower()]
    def __str__(self):
        string  = "MLS:             {0}\n".format(self.MLS)
        string += "Status:          {0}\n".format(self.Status)
        string += "Address:         {0}\n".format(self.Address)
        string += "Price:           ${0:.2f}\n".format(self.Price)
        string += "Taxes:           ${0:.2f}\n".format(self.Taxes)
        string += "HOA:             ${0:.2f}\n".format(self.HOA)
        try:
            string += "Work Mileage:    {0}\n".format(self.distances['work'])
        except KeyError:
            pass
        return string
    def status(self):
        try:
            return self.Status.lower()
        except:
            return "active"
    def __eq__(self, other):
        if self.MLS.upper() == other.MLS.upper() and \
            "{0:.2f}".format(self.Price) == "{0:.2f}".format(other.Price):
            return True
        return False
    def __ne__(self, other):
        return not self.__eq__(other)
