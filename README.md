# fantasy-fball-aav-web-scraper

For fantasy football managers participating in auction-style drafts, [Yahoo Fantasy Football](https://football.fantasysports.yahoo.com) allows team managers to provide their own custom salary cap values prior to their league's draft. Users can set personal auction values for as many players as they'd like and exclude certain players they are not interested in drafting. Projected auction values are also displayed based on league settings.

![Yahoo Fantasy Football Pre-Draft Auction Costs](/_img/yahoo_pre_draft_auction_values.png)

While this is valuable data, this section of the Yahoo Fantasy Football platform does not allow managers to annotate and add their own notes for each player. I created this small app to scrape these pre-draft average auction values on an annual basis using [Selenium](https://github.com/SeleniumHQ/selenium) and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup). The pre-draft fantasy football auction values get extracted to a CSV flat file, which I then convert to a spreadsheet for further annotation and analysis.