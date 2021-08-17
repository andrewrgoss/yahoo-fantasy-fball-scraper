# Yahoo Fantasy Football Pre-Draft Auction Values Scraper

For fantasy football managers participating in auction-style drafts, [Yahoo Fantasy Football](https://football.fantasysports.yahoo.com) allows team managers to provide their own custom salary cap values prior to their league's draft. Users can set personal auction values for as many players as they'd like and exclude certain players they are not interested in drafting. Projected auction values are also displayed based on league settings.

![Yahoo Fantasy Football Pre-Draft Auction Costs](/_img/yahoo_pre_draft_auction_values.png)

While this is valuable data, this section of the Yahoo Fantasy Football platform does not allow managers to annotate and add their own notes for each player. I created this small app to scrape these pre-draft average auction values on an annual basis using [Selenium](https://github.com/SeleniumHQ/selenium) and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup). The pre-draft fantasy football auction values get extracted to a CSV flat file, which I then convert to a spreadsheet for further annotation and analysis.

## Usage

This app is designed to be used using a Mac computer that remotely controls your [Safari](https://www.apple.com/safari/) web browser. Download this repository, and run the following command:

`/<<your_local_download_location>>/fantasy-fball-aav-web-scraper/main.py --yahoo_email <<your_yahoo_email>> --yahoo_pw <<your_yahoo_password>> --yahoo_league_id <<your_yahoo_fantasy_football_league_id>>`

Your Yahoo Fantasy Football league ID can be found in the URL from your league home page: https://football.fantasysports.yahoo.com/f1/######