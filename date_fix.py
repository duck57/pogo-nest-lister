#!/usr/bin/env python3
# coding=UTF-8
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import os
import sqlite3
import importoldlists as dbutils


dbfile = "nests.db"
dbc = dbutils.create_connection(dbfile)
if dbc is None:
	print("Error creating database")
	sys.exit(1)

dates = dbc.execute("SELECT * FROM rotation_dates WHERE num<>`order`").fetchall()
for date in dates:
	if date[0] == 0:
		continue
	species = dbc.execute("SELECT * FROM species_list WHERE rotation_num = ?", [date[0]]).fetchall()
	print("Renaming rotation " + str(date[0]) + " to " + str(date[3]) + " and moving " + str(len(species)) + " records")
	dbc.execute("UPDATE species_list SET rotation_num = 0 WHERE rotation_num = ?", [date[0]])
	dbc.execute("UPDATE rotation_dates SET num = `order` WHERE num = ? AND `order` = ?", [date[0], date[3]])
	dbc.execute("UPDATE species_list SET rotation_num = ? WHERE rotation_num = 0", [date[3]])

dbc.commit()