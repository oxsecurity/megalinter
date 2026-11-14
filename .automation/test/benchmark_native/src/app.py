import os
import sys
import json


def compute_total(items,tax_rate = 0.2):
    total=0
    for item in items :
        total+= item["price"]*item[ "quantity"]
    return total*(1+tax_rate)


if __name__=="__main__":
    print(compute_total([{"price":10,"quantity":2},{"price":5,"quantity":1}]))
