# Yahoo Fantasy Football Scraper

For fantasy football managers using Yahoo! for season-long leagues, there is a lot of valuable data residing in the web interface that can help you prepare for the all-important preseason draft. While Yahoo does have an API, [its available methods](https://yahoo-fantasy-api.readthedocs.io/en/latest/yahoo_fantasy_api.html) are missing some key datapoints. Enter web scraping.

Using [Selenium](https://github.com/SeleniumHQ/selenium) and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup), I created some scripts to extract pre-draft auction values and player season projections. These generate CSV flat files that are sortable by various player details, which I then convert to different spreadsheets for further annotation and analysis.

## Extract Historical League Auction Draft Results for Analysis

Examining a specific fantasy football league's auction draft history over several years can give a gauge into how different managers may approach player bidding. It can also highlight typical values for players going in a particular range (ex. average auction price for the 10th running back drafted).

![Yahoo Fantasy Football Historical Draft Results](/_img/yahoo_historical_draft_results.png)

## Extract Pre-Draft Auction Values for Analysis

For fantasy football managers participating in auction-style drafts, [Yahoo Fantasy Football](https://football.fantasysports.yahoo.com) allows team managers to provide their own custom salary cap values prior to their league's draft. Users can set personal auction values for as many players as they'd like. Average, league, and projected auction values are also displayed based on league settings. While this is valuable data, this section of the Yahoo Fantasy Football platform does not allow managers to annotate their own notes for each player. 

![Yahoo Fantasy Football Pre-Draft Auction Costs](/_img/yahoo_pre_draft_auction_values.png)

## Extract Player Season Projections for Analysis

Yahoo's season-long projected fantasy points by player, while an imperfect methodology, can be useful to identify good/bad player values based on projected fantasy point outputs vs. expected acquisition cost.

![Yahoo Fantasy Football Player Season-Long Projections](/_img/yahoo_player_acquistion_values_based_on_season_projections.png)

## Extract Current League Auction Draft Results for Analysis

After your draft completes, this script can be run to extract the results of your auction-style draft. With this data, you can determine which managers got the best/worst values based on expected auction values.

## Usage

These scripts are designed to be used with a Mac computer that remotely controls your [Safari](https://www.apple.com/safari/) web browser. It's not designed to work with Yahoo 2-step verification (2sv) and this should be disabled, at least temporarily. Your Yahoo Fantasy Football league ID can be found in the URL from your league home page: https://football.fantasysports.yahoo.com/f1/######

Download this repository and run the following commands:

#### Historical League Auction Draft Results
`/<<your_local_download_location>>/yahoo-fantasy-fball-scraper/historical_draft_results.py --yahoo_email <<your_yahoo_email>> --yahoo_pw <<your_yahoo_password>> --yahoo_league_name <<your_yahoo_fantasy_football_league_name>> --yahoo_league_year <<historical_year_to_lookup_your_league_draft_results>>`

#### Predraft Auction Values
`/<<your_local_download_location>>/yahoo-fantasy-fball-scraper/predraft_auction_values.py --yahoo_email <<your_yahoo_email>> --yahoo_pw <<your_yahoo_password>> --yahoo_league_id <<your_yahoo_fantasy_football_league_id>>`

#### Player Current Season Projections
`/<<your_local_download_location>>/yahoo-fantasy-fball-scraper/player_season_projections.py --yahoo_email <<your_yahoo_email>> --yahoo_pw <<your_yahoo_password>> --yahoo_league_id <<your_yahoo_fantasy_football_league_id>> --yahoo_league_year <<current_year_to_lookup_season_long_projections>>` 

#### Current League Auction Draft Results
`/<<your_local_download_location>>/yahoo-fantasy-fball-scraper/current_draft_results.py --yahoo_email <<your_yahoo_email>> --yahoo_pw <<your_yahoo_password>> --yahoo_league_id <<your_yahoo_fantasy_football_league_id>>`