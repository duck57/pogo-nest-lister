CREATE TABLE IF NOT EXISTS nest_locations (
	nest_id integer PRIMARY KEY,
	official_name text NOT NULL,
	short_name text,
	alternate_names text,
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
);

CREATE TABLE IF NOT EXISTS rotation_dates (
	num integer PRIMARY KEY,
	date text NOT NULL,
	special_note text
);

CREATE TABLE IF NOT EXISTS species_list (
	rotation_num integer NOT NULL,
	nestid integer NOT NULL,
	species_txt text,
	species_no integer,
	confirmation integer,
	FOREIGN KEY (rotation_num) REFERENCES rotation_dates (num),
	FOREIGN KEY (nestid) REFERENCES nest_locations (nest_id),
	PRIMARY KEY (rotation_num, nestid)
);

CREATE TABLE IF NOT EXISTS neighborhoods (
	id integer PRIMARY KEY,
	name text NOT NULL,
	region integer,
	lat real,
	lon real,
	FOREIGN KEY (region) REFERENCES regions (id)
);

CREATE TABLE IF NOT EXISTS regions (
	id integer PRIMARY KEY,
	name text NOT NULL
);

CREATE TABLE IF NOT EXISTS alt_names (
	name text NOT NULL,
	main_entry integer NOT NULL,
	FOREIGN KEY (main_entry) REFERENCES neighborhoods (id)
)