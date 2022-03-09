# db migrations

Script as much of the below as possible

1. delete the db
1. clear and all migration files in all apps
1. create the db
1. inject the production sql
	1. may have to tweak the db -- i had to run `sed -i '' 's/utf8mb4_0900_ai_ci/utf8mb4_unicode_ci/g' PRODFILENAME.SQL`
1. overwrite all models.py files with production's versions
1. run makemigrations
1. overwrite all models.py files with this repo's versions
1. run makemigrations again to bring this up to date with the api
1. run supplemental corrections
	1. all date fields should be split to mm dd yyyy field triples (see dates_to_mdy_cols.py)
	1. the prod sql has some weird vestigia b/c of hard-coded values, so there's gonna be more

