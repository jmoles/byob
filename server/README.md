Heroku Provision Server
=======================
This folder contains the source for the provisioning server that is ready to deploy on heroku and has files that can be tested on foreman. Full directions on deploying a Ruby application to Heroku can be found at https://devcenter.heroku.com/articles/ruby.

Here are some steps that are close to what needs to happen:

1. Rename .env_sample to .env and set variables in file.
2. Also, configure these variables on Heroku by running (replacing demo):
	heroku config:set GAME_PASS=demo
	heroku config:set PUBNUB_SUBSCRIBE=demo
	heroku config:set PUBNUB_PUBLISH=demo
	heroku config:set PUBNUB_SECRET=demo
3. Run 
	bundle install
4. Initialize a new Heroku repository and run
	heroku create
5. Push this code to the master branch of heroku repository.
