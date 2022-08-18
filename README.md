# Yahoo Fantasy Football Auction Values Scraper: Pre-Draft and Historical League Drafts

## Extract Pre-Draft Auction Values for Analysis

For fantasy football managers participating in auction-style drafts, [Yahoo Fantasy Football](https://football.fantasysports.yahoo.com) allows team managers to provide their own custom salary cap values prior to their league's draft. Users can set personal auction values for as many players as they'd like. Average, league, and projected auction values are also displayed based on league settings. While this is valuable data, this section of the Yahoo Fantasy Football platform does not allow managers to annotate and add their own notes for each player. 

![Yahoo Fantasy Football Pre-Draft Auction Costs](/_img/yahoo_pre_draft_auction_values.png)

I created this small script to scrape these pre-draft average auction values on an annual basis using [Selenium](https://github.com/SeleniumHQ/selenium) and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup). The pre-draft fantasy football auction values - along with sortable player details including name, team, position, and your league's previous owner - get extracted to a CSV flat file, which I then convert to a spreadsheet for further annotation and analysis.

### Usage

This app is designed to be used with a Mac computer that remotely controls your [Safari](https://www.apple.com/safari/) web browser. It's not designed to work with Yahoo 2-step verification (2sv) and this should be disabled, at least temporarily. Auction value data for 50 players at a time will be extracted to the CSV output for the top 300 players.

Download this repository and run the following command:

`/<<your_local_download_location>>/yahoo-fantasy-fball-auction-value-scraper/predraft_auction_values.py --yahoo_email <<your_yahoo_email>> --yahoo_pw <<your_yahoo_password>> --yahoo_league_id <<your_yahoo_fantasy_football_league_id>>`

Your Yahoo Fantasy Football league ID can be found in the URL from your league home page: https://football.fantasysports.yahoo.com/f1/######

## Extract Historical League Auction Draft Results for Analysis

Examining a specific fantasy football league's auction draft history over several years can give a barometer into how different managers approach player bidding. It can also highlight typical values for players going in a particular range (ex. average auction price for the 10th running back drafted).

I created this small script to scrape a player's historical league auction draft results for different supplied years using [Selenium](https://github.com/SeleniumHQ/selenium) and [Pandas](https://pandas.pydata.org). The historical fantasy football auction draft results for past leagues you've participated in - along with sortable player details including name, team, position, and your league's winning bid owner - get extracted to a CSV flat file, which I then convert to a spreadsheet for further annotation and analysis.

### Usage

This app is designed to be used with a Mac computer that remotely controls your [Safari](https://www.apple.com/safari/) web browser. It's not designed to work with Yahoo 2-step verification (2sv) and this should be disabled, at least temporarily.

Download this repository and run the following command:

`/<<your_local_download_location>>/yahoo-fantasy-fball-auction-value-scraper/predraft_auction_values.py --yahoo_email <<your_yahoo_email>> --yahoo_pw <<your_yahoo_password>> --yahoo_league_name <<your_yahoo_fantasy_football_league_name>> --yahoo_league_year <<historical_year_to_lookup_your_league_draft_results>>`