# Small Notion API

A small API for sending text to notion. Using the awesome python notion package which calls the unofficial Notion API to create new things.

Also adding cron jobs to run every day, every monday, every firt of the month to create new pages for me.


## Usage

Adjust your AWS creds in `serverless.yml` and run `serverless deploy`

The you need to adjust the env variables on the lambda functions.  
Most importantly your `NOTION_TOKEN` and the `API_SECRET`

Then you'll have an enpoint `/create` where you can post your content to
