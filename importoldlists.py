#!/usr/bin/env python3
# coding=UTF-8
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import sqlite3
from sqlite3 import Error
import sort
import csv
import sys
import os


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


# sets up the database
def setup_db(conn):
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
                                        FOREIGN KEY (main_entry) REFERENCES neighborhoods (id)
                                )"""

    # create the region list
    create_table(conn, sql_create_region_table)
    # create the neighborhoods list
    create_table(conn, sql_create_neighborhood_table)
    # create nest location table
    create_table(conn, sql_create_nests_table)
    # create date table
    create_table(conn, sql_create_rotations_table)
    # create the master species list
    create_table(conn, sql_create_species_table)
    # set up table of alternate names
    create_table(conn, sql_create_altname_table)


# insert a row into the neighborhood table
def add_neighborhood(nname, dbcon):
    sql = """INSERT INTO neighborhoods(name)
        VALUES(?) """
    cur = dbcon.cursor()
    cur.execute(" INSERT INTO neighborhoods(name) VALUES(?) ", [nname])
    return cur.lastrowid


# returns the neighborhood ID
def query_neighborhood(neighborhood, dbcon):
    cur = dbcon.cursor()
    cur.execute("SELECT id FROM neighborhoods WHERE name LIKE ?", (neighborhood,))
    result = cur.fetchall()
    if len(result) > 1:
        print("Error!  Multiple matches found for \"" + neighborhood + "\".  Using first match.")
    if len(result) == 0:
        # print("No matches found for " + neighborhood)  # uncomment for debugging
        return None
    return result[0][0]

# insert a row to the alternate name table
def new_alt_names(altnames, parentID, dbcon):
    altlst = altnames.split("/")
    cur = dbcon.cursor()
    for alt in altlst:
        cur.execute("INSERT INTO alt_names(main_entry, name) VALUES(?,?)", (parentID, alt))


# insert a row into the nest table
# assumes no duplicate nests in the list
# many of these variables are made simply to make the code more readable
def add_nest(nestdict, dbcon):
    # prepare for NULL values
    for key in nestdict.keys():
        if nestdict[key].strip() == "":
            nestdict[key] = None

    # easier to read
    oname = nestdict["Official Name"]
    sname = nestdict["Short Name"]
    altnames = nestdict["Alternate Names"]
    neighborhood = nestdict["Location"]
    notes = nestdict["Notes"]
    private = nestdict["Private Property?"]
    perm_nest = nestdict["Species"]
    nid = None

    # data wrangling
    if neighborhood is not None:
        nid = query_neighborhood(neighborhood, dbcon)
        if nid is None:
            nid = add_neighborhood(neighborhood, dbcon)
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
    cur = dbcon.cursor()
    cur.execute(sql, nest_tuple)
    nestid = cur.lastrowid
    if altnames is not None:
        new_alt_names(altnames, nestid, dbcon)
    return nestid


# reads a tsv city nest list into the DB
# this assumes the soon to be removed "new" TSV formatting
# As the new never got used in production, the history import uses the old/current TSV format
def import_city(cfile, dbcon):
    cmem = open(cfile, "r")
    nestin = csv.DictReader(cmem, delimiter="\t")
    for nest in nestin:
        add_nest(nest, dbcon)
    cmem.close()


# also add some city selection code soon
def main():
    cfile = sort.choose_city(None)
    cname = cfile.split("/")[1][:-len(sort.ext)]  # just the name
    database = cname + ".db"
    conn = create_connection(database)
    if conn is None:
        print("Error creating database")
        return None
    setup_db(conn)

    # comment out the below three lines if you have successfully imported the nest list
    # but had trouble importing the historical nest data
    import_city(cfile, conn)
    conn.commit()
    print("Successfully imported nest list from " + cfile + " into database " + database)

    print("Attempting to ")


if __name__ == '__main__':
    main()
