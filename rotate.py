#!/usr/bin/env python3
# coding=UTF-8
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import datetime  # as dateutil
import os

import click
from dateutil.parser import *
from dateutil.relativedelta import *

import importoldlists as dbutils
import sort

# Creates a new nest list in the hist-list/<CITY> folder with a YYYY-MM-DD name


outpath = "hist-list/"
city = None
date = None


# Probably can share more code with sort.py methods
# but they're slightly different
def val_city(city=None):
    cpath = sort.choose_city(city + sort.ext)  # path to the city's template file
    city2 = cpath.split("/")[1][:-len(sort.ext)]  # just the city name
    return cpath, city2


# checks that a directory exists and creates it if it does not
def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Initialized nest folder at " + directory)


# returns the expanded command for a relativedate statement
def expand8(chr):
    return {
        'y': "years",
        'm': "months",
        'w': "weeks",
        't': "days"
    }.get(chr, 0)


# checks if a string will convert to an int
# why isn't this in the standard library?
def str_int(str):
    try:
        int(str)
    except ValueError:
        return False
    return True


# gets a date (also accepts relative dates like y-1, t+3, w+2)
def getdate(date=None):
    today = datetime.datetime.today()
    while True:
        if date is None:
            date = input("What is the date of the nest rotation (blank for today, " + str(today.date()) + ")? ")
        if date.strip() == "" or (len(date) == 1 and date[0].lower() == "t"):
            return today.date()
        if date[0].lower() in "ymwt" and len(date) > 2 and date[1] in "+-" and str_int(date[1:]):
            dateshift = int(date[1:])
            units = date[0].lower()
            # print("shifting by " + str(dateshift) + " " + expand8(units))
            createdate = today + {
                'y': relativedelta(years=dateshift),
                'm': relativedelta(months=dateshift),
                'w': relativedelta(weeks=dateshift),
                't': relativedelta(days=dateshift)
            }.get(units, 0)
            return createdate.date()
        try:
            return parse(date).date()
        except (ValueError, TypeError):
            print("Please enter a valid date.")
            date = input("What is the date of the nest rotation (blank for today, " + str(today.date()) + ")? ")


@click.command()
@click.option(
    '-d',
    '--date',
    default=str(datetime.datetime.today().date()),
    prompt="Date of nest shift",
    help="Date when the nest shift occured, can be absolute (YYYY-MM-DD) or relative (w+2)"
)
# main method
def main(date):
    d8 = str(getdate(date.strip()))
    dbc = dbutils.create_connection("nests.db")
    d8tst = "SELECT * FROM rotation_dates WHERE date LIKE ?"
    cur = dbc.cursor()
    cur.execute(d8tst, [d8])
    if len(cur.fetchall()) > 0:
        print("Rotation already exists for " + d8)
        return
    add8 = "INSERT INTO rotation_dates(date) VALUES(?)"
    cur.execute(add8, [d8])
    rotnum = cur.lastrowid
    perm_nst = "SELECT nest_id, permanent_species FROM nest_locations WHERE permanent_species IS NOT NULL"
    cur.execute(perm_nst)
    permanent = cur.fetchall()
    add_prm = "INSERT INTO species_list(rotation_num, nestid, species_txt, confirmation) VALUES(?,?,?,1) "
    for perm in permanent:
        cur.execute(add_prm, (rotnum, perm[0], perm[1]))
    print("Added rotation " + str(rotnum) + " on " + d8)
    dbc.commit()


if __name__ == "__main__":
    main(None, None)
