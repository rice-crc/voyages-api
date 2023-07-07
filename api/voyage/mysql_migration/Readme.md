From scratch

1. Use the production models, which I've given the suffix "old"
	1. They're approx [here](https://github.com/JohnMulligan/voyages-api/commit/9c83c1a821ab99f5be9e0b221b689f6dec23ab71#diff-b6c7c6c2b43303970a522afd81203c5dc5f4614ca8c9e785f2c2ee774fac382f)
	1. disable
		1. all serializers
		1. all admin interfaces
	1. remove documents & geo apps from 
		1. installed apps
		1. urls.py
	1. remove rest framework from installed apps
1. migrate. ONLY MIGRATE, USING THE 0001 INIT VALUES
1. create another db in the mysql container named "voyages voyages past merge"
1. inject the prod db into this new db
1. run the custom script in this folder
1. bring document and geo apps online
1. migrate and makemigrations
1. re-instate the new models
1. migrate and makemigrations
1. re-enable
	1. the urls
	1. the admin interfaces
	1. the serializers