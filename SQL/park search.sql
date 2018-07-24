SELECT nest_id, official_name, short_name, location, an.name AS altnm
FROM nest_locations AS nl LEFT OUTER JOIN alt_names AS an
ON nl.nest_id = an.main_entry
WHERE (official_name LIKE '%Worthington%' OR short_name LIKE '%Worthington%' OR an.name LIKE '%Worthington%') --AND nl.location = 2