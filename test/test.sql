select s.path, s.id, title, s.type, s.size, length, language, genre, year, null as artist, null as album, watched, null as franchise, null as installment, show_name, season, episode,
o.path as new_path, o.parent_path
from shows s, organised o
where s.id = o.id
UNION
select f.path, f.id, title, f.type, f.size, length, language, genre, year, null as artist, null as album, watched, franchise, installment, null as show_name, null as season, null as episode, 
o.path as new_path, o.parent_path
from films f, organised o
where f.id = o.id
UNION
select s.path, s.id, title, s.type, s.size, length, language, genre, year, artist, album, null as watched, null as franchise, null as installment, null as show_name, null as season, null as episode, 
o.path as new_path, o.parent_path
from songs s, organised o
where s.id = o.id
UNION
select fp.media_path as path, fp.id, null as title, fp.type, fp.size, null as length, null as language, null as genre, null as year, null as artist, null as album,
null as watched, null as franchise, null as installment, null as show_name, null as season, null as episode,
o.path as new_path, o.parent_path
from file_props fp, organised o
where fp.id = o.id
and fp.type = "media_dir"
