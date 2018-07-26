--template for searching for a park by name matching any of the name fields
SELECT nest_id, official_name, short_name, location, an.name AS altnm
FROM nest_locations AS nl LEFT OUTER JOIN alt_names AS an
ON nl.nest_id = an.main_entry
WHERE (official_name LIKE '%Worthington%' OR short_name LIKE '%Worthington%' OR an.name LIKE '%Worthington%') --AND nl.location = 2


--template to select all the nests for the current rotation
SELECT
	sl.species_txt AS Species
	,sl.confirmation AS 'Confirmed?'
	,nls.nest_id
	,nls.official_name AS 'Primary Name'
	,nls.short_name AS 'Short Name'
	,nls.notes AS 'Park Notes'
	,nls.private AS 'Private Property?'
	,nbz.name AS 'Neighborhood'
	,regions.name AS 'Location'
FROM species_list AS sl
	LEFT OUTER JOIN nest_locations AS nls ON (sl.nestid = nls.nest_id)
	LEFT OUTER JOIN neighborhoods AS nbz ON (nls.location = nbz.id)
	LEFT OUTER JOIN regions ON (nbz.region = regions.id)
WHERE sl.rotation_num = 11

--select all nests that aren't in a current rotation
--comment out the WHERE rotation_num = ? part to get a list of all nests that have never had a report
SELECT
	nls.nest_id
	,nls.official_name AS 'Primary Name'
	,nls.short_name AS 'Short Name'
	,nbz.name AS 'Neighborhood'
	,regions.name AS 'Location'
FROM nest_locations AS nls
	LEFT OUTER JOIN neighborhoods AS nbz ON (nls.location = nbz.id)
	LEFT OUTER JOIN regions ON (nbz.region = regions.id)
WHERE nls.nest_id NOT IN (
	SELECT nestid FROM species_list
	WHERE rotation_num = 10
)

--selects everything but the alt names that would be displayed on a nest editing screen
SELECT
	nest_locations.*,
	neighborhoods.name AS 'Subdivision',
	regions.*
FROM nest_locations
	LEFT OUTER JOIN neighborhoods ON nest_locations.location = neighborhoods.id
	LEFT OUTER JOIN regions ON neighborhoods.region = regions.id
WHERE nest_id = ?