create view if not exists search as
select id, group_concat(title, '') as title, type, size, max(length), group_concat(language, '') as language, group_concat(genre, '') as genre, max(year), path as real_path, group_concat(new_path, '') as new_path from 
(select distinct (media_path or sys_path) as path, id, null as title, type, size, null as length, null as language, null as genre, null as year, null as new_path from file_props
union
select distinct *, null as new_path from media group by id
union
select null as path, id, null as title, type, size, null as length, null as language, null as genre, null as year, path as new_path from organised)
group by id

-- select * from media union (select id, media_path, null, type, size, null, null, null, null from file_props where type = "media_dir")

-- create procedure extension(file text) AS
-- begin

-- select substr(file, instr(file, ".") + 1);

-- end;
