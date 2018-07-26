#!/usr/bin/env python3
# coding=UTF-8
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import sqlite3
from sqlite3 import Error
import csv
import sys
import os
from dateutil.parser import *

# this has helper functions in all 3 other files
import sort
import update
import rotate


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        dbc = sqlite3.connect(db_file)
        return dbc
    except Error as e:
        print(e)

    return None


def create_table(dbc, create_table_sql):
    """ create a table from the create_table_sql statement
    :param dbc: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = dbc.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


# sets up the database
def setup_db(dbc):
    sql_create_nests_table = """ CREATE TABLE IF NOT EXISTS nest_locations (
                                        nest_id integer PRIMARY KEY AUTOINCREMENT,
                                        official_name text NOT NULL,
                                        short_name text,
                                        location integer,
                                        address text,
                                        notes text,
                                        private integer,
                                        permanent_species text,
                                        lat real,
                                        lon real,
                                        size integer,
                                        density integer,
                                        FOREIGN KEY (location) REFERENCES neighborhoods (id)
                                 ); """

    sql_create_rotations_table = """CREATE TABLE IF NOT EXISTS rotation_dates (
                                        num integer PRIMARY KEY AUTOINCREMENT,
                                        date text NOT NULL,
                                        special_note text
                                );"""

    sql_create_species_table = """CREATE TABLE IF NOT EXISTS species_list (
                                        rotation_num integer NOT NULL,
                                        nestid integer NOT NULL,
                                        species_txt text,
                                        species_no integer,
                                        confirmation integer,
                                        FOREIGN KEY (rotation_num) REFERENCES rotation_dates(num),
                                        FOREIGN KEY (nestid) REFERENCES nest_locations(nest_id),
                                        PRIMARY KEY (rotation_num, nestid)
                                );"""

    sql_create_neighborhood_table = """CREATE TABLE IF NOT EXISTS neighborhoods (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text NOT NULL,
                                        region integer,
                                        lat real,
                                        lon real,
                                        FOREIGN KEY (region) REFERENCES regions (id)
                                );"""

    sql_create_region_table = """CREATE TABLE IF NOT EXISTS regions (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text NOT NULL
                                );"""
    sql_create_altname_table = """CREATE TABLE IF NOT EXISTS alt_names (
                                        name text NOT NULL,
                                        main_entry integer NOT NULL,
                                        hideme integer,
                                        FOREIGN KEY (main_entry) REFERENCES nest_locations (nest_id)
                                )"""

    # create the region list
    create_table(dbc, sql_create_region_table)
    # create the neighborhoods list
    create_table(dbc, sql_create_neighborhood_table)
    # create nest location table
    create_table(dbc, sql_create_nests_table)
    # create date table
    create_table(dbc, sql_create_rotations_table)
    # create the master species list
    create_table(dbc, sql_create_species_table)
    # set up table of alternate names
    create_table(dbc, sql_create_altname_table)


# insert a row into the neighborhood table
def add_neighborhood(nname, dbc):
    sql = """INSERT INTO neighborhoods(name)
        VALUES(?) """
    cur = dbc.cursor()
    cur.execute(" INSERT INTO neighborhoods(name) VALUES(?) ", [nname])
    return cur.lastrowid


# returns the neighborhood ID
def query_neighborhood(neighborhood, dbc):
    if neighborhood.strip() == '':
        return None
    cur = dbc.cursor()
    cur.execute("SELECT id FROM neighborhoods WHERE name LIKE ?", ['%' + neighborhood + '%'])
    result = cur.fetchall()
    if len(result) > 1:
        print("Error!  Multiple matches found for \"" + neighborhood + "\".  Using first match.")
    if len(result) == 0:
        # print("No matches found for " + neighborhood)  # uncomment for debugging
        return None
    return result[0][0]

# insert a row to the alternate name table
def new_alt_names(altnames, parentID, dbc):
    altlst = altnames.split("/")
    cur = dbc.cursor()
    for alt in altlst:
        cur.execute("INSERT INTO alt_names(main_entry, name) VALUES(?,?)", (parentID, alt))


# insert a row into the nest table
# assumes no duplicate nests in the list
# many of these variables are made simply to make the code more readable
def add_nest(nestdict, dbc):
    # prepare for NULL values
    for key in nestdict.keys():
        if nestdict[key].strip() == "":
            nestdict[key] = None

    # easier to read, accommodates old-style lists
    if "Short Name" in nestdict.keys():
        oname = nestdict["Official Name"]
        sname = nestdict["Short Name"]
        altnames = nestdict["Alternate Names"]
    else:
        oname = nestdict["Primary Name"]
        sname = None
        altnames = nestdict["Alternate Name"]
    neighborhood = nestdict["Location"]
    notes = nestdict["Notes"]
    private = nestdict["Private Property?"]
    perm_nest = nestdict["Species"]
    nid = None

    # data wrangling
    if neighborhood is not None:
        nid = query_neighborhood(neighborhood, dbc)
        if nid is None:
            nid = add_neighborhood(neighborhood, dbc)
    if private is not None:
        if private[0].lower() == 'y':
            private = 1
        elif private[0].lower() == 'n':
            private = 0
        elif private.isnumeric:
            private = int(private)
        else:
            private = None

    nest_tuple = (oname, sname, nid, notes, private, perm_nest)
    # print(nest_tuple)
    sql = """INSERT INTO nest_locations(official_name, short_name, location,
                notes, private, permanent_species)
                VALUES(?,?,?,?,?,?)"""
    cur = dbc.cursor()
    cur.execute(sql, nest_tuple)
    nestid = cur.lastrowid
    if altnames is not None:
        new_alt_names(altnames, nestid, dbc)
    return nestid


# reads a tsv city nest list into the DB
# this assumes the soon to be removed "new" TSV formatting
# As the new never got used in production, the history import uses the old/current TSV format
def import_city(cfile, dbc):
    cmem = open(cfile, "r")
    nestin = csv.DictReader(cmem, delimiter="\t")
    for nest in nestin:
        add_nest(nest, dbc)
    cmem.close()


# searches for a nest and returns matching results and the neighborhood ID
# each result in the returned list is in tuplet form:
# (nest_id, official_name, short_name, neighborhood_id, altname)
# can be restricted by neighborhood
def query_nest(search, dbc, area=None):
    if search.strip == '':  # don't return everything if you search for nothing
        return None, area
    cur = dbc.cursor()
    search = '%' + search + '%'
    query = """SELECT nest_id, official_name, short_name, location, an.name AS altnm
        FROM nest_locations AS nl LEFT OUTER JOIN alt_names AS an
        ON nl.nest_id = an.main_entry
        WHERE (official_name LIKE ? OR short_name LIKE ? OR an.name LIKE ?) """
    addendum = " AND nl.location = ?"
    tuple = (search, search, search)

    try:
        if not area.isnumeric():
            area = query_neighborhood(area, dbc)
    except (AttributeError):
        pass  # when None is passed in
    if area is not None:
        query = query + addendum
        tuple = (search, search, search, area)

    cur.execute(query, tuple)
    results = cur.fetchall()
    if len(results) == 0:
        # print("No results found for " + search + " in " + str(area))
        return None, area
    if len(results) > 1:
        # print("Multiple matches found for " + search + " in " + str(area) + ", returning top result")
        pass
    # print(results)  # debug stuff
    return results, area


# fuzzy nest matching on name and neighborhood
# will return a match if on a name match if there is neighborhood mismatch
# if there are multiple name results, attempt to match on neighborhood as well as name
def nandn_nmatch(nameq, lid, dbc):
    nids, _ = query_nest(nameq, dbc, None)
    if nids is None:  # no results
        return nids
    if len(nids) == 1:  # one result
        return nids[0][0]
    for test in nids:  # pick the first result with the correct neighborhood
        if test[3] == lid:
            return test[0]
    return nids[0][0]  # multiple results and no location exact matches


# looks up a nest by name from the spreadsheets
# returns the nest ID if it's found or None otherwise
# there has to be a better way to organize this logic
def findanest(nestdict, dbc):
    key_list = ["Official Name", "Short Name", "Primary Name"]
    headers = nestdict.keys()
    n = None
    loc = query_neighborhood(nestdict["Location"], dbc)

    for nametype in key_list:
        if nametype in headers:
            n = nandn_nmatch(nestdict[nametype], loc, dbc)
            if n is None:
                continue
            return n

    altlst = ["Alternate Name", "Alternate Names"]
    for althead in altlst:
        if althead in headers:
            for altnm in nestdict[althead].split("/"):
                if altnm != "":
                    n = nandn_nmatch(altnm, loc, dbc)
    return n


# adds a specific old nest to the database
def add_old_nest(nestd, d8, d8id, dbc):
    if nestd["Species"].strip() == '':
        return
    nstid = findanest(nestd, dbc)
    if nstid is None:
        print("Cannot find matching nest ID for row " + str(nestd) + " on date " + d8 + " rotation #" + str(d8id))
        return
    sqins = """INSERT INTO species_list(rotation_num, nestid, species_txt, confirmation)
               VALUES(?,?,?,?)"""
    cur = dbc.cursor()
    con = nestd["Confirm?"]
    if len(con) > 0 and update.true_if_Y(con):
        con = 1
    else:
        con = None

    params = (d8id, nstid, nestd["Species"], con)
    try:
        cur.execute(sqins, params)
    except (sqlite3.IntegrityError):
        print("Duplicate nest entries for nest #" + str(nstid) + " on " + d8 + " rot#" + str(d8id))
    except (sqlite3.InterfaceError):
        print("Something went wrong with " + str(params) + " on " + d8 + " rot#" + str(d8id))


# adds an old rotation to add it to the DB
def add_old_rotation(file, date, dbc):
    # get a rotation ID
    cur = dbc.cursor()
    cur.execute("INSERT INTO rotation_dates(date) VALUES(?)", [date])
    dateID = cur.lastrowid
    # print("Rotation on " + date + " has ID " + str(dateID))

    # deal with the file
    fin = open(file, 'r')
    nestlist = csv.DictReader(fin, delimiter="\t")
    for nest in nestlist:
        add_old_nest(nest, date, dateID, dbc)
    fin.close()
    dbc.commit()  # commit DB changes in case things error badly on the next file


# goes through a folder of old nest lists and chucks out most invalid files before
# sending them to add_old_rotation
def import_old_lists(cfolder, dbc):
    for file in os.listdir(cfolder):
        fnm = file.split(".")[0]
        if fnm.strip() == '' or not os.path.isfile(cfolder + file):
            print("Skipping junk file " + file)
            continue  # skip .DS_Store and subdirectories

        try:  # ensure it's a valid date
            d8 = parse(fnm)
        except (TypeError, ValueError):
            print("Cannot determine date associated with " + file + ".")
            instr = "Enter a valid date to import the data in " + file + " under or enter junk to skip importing " + file
            try:
                d8 = parse(input(instr))
            except (ValueError, TypeError):
                continue
        d8str = str(d8).split(" ")[0]

        # skip previously-imported lists in case of retries due to errors
        cur = dbc.cursor()
        cur.execute("SELECT num FROM rotation_dates WHERE date LIKE ?", (d8str,))
        result = cur.fetchall()
        if len(result) > 0:
            print("Skipping import of " + file + " because a rotation for " + d8str + " is already imported")
            continue
        else:
            add_old_rotation(cfolder + file, d8str, dbc)


# main method
def main():
    cfile = sort.choose_city(None)
    cname = cfile.split("/")[1][:-len(sort.ext)]  # just the name
    database = cname + ".db"
    dbc = create_connection(database)
    if dbc is None:
        print("Error creating database")
        return None
    setup_db(dbc)

    # comment out the below three lines if you have successfully imported the nest list
    # but had trouble importing the historical nest data
    import_city(cfile, dbc)
    dbc.commit()
    print("Successfully imported nest list from " + cfile + " into database " + database)

    archivefolder = "hist-list/"
    cityfolder = archivefolder + cname + "/"
    print("Attempting to import historical migration data…")
    if not update.city_folder_check(cname, archivefolder):
        return  # ensures there will be actual nest data to import
    import_old_lists(cityfolder, dbc)
    dbc.commit()  # maybe I need to do it here?
    print("Imported nest data for " + cname + ".\nRename the output .db file to nests.db to use it as the main database in the future.")


if __name__ == '__main__':
    main()
