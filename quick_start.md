Matthew Gwilliam

mgwillia@umd.edu

# Installation and Setup

1. Install packages: `pip install flask psycopg2` (I installed no new packages, only what was used for a1)
2. Run `randomizer.py 1000000` (any number can be used, doesn't have to be 1 million). **This script handles all setup**: it generates the records, uploads them to the DB, and sets up DB objects related to my optimizations. For a million records, it will take a minute or two to run. Note that my randomizer doesn't just repeat rows, instead it samples randomly for various fields, with random augmentations for the numerical attributes, preserving the critical relationships between position, year, and the stats. I have included the two csv source tables (`nba_player_seasons.csv` and `player_data.csv`) and the preprocessing file (`preprocess.py`) for completeness, but they are not required for setup. The code assumes database (`a3database`) and user (`cmsc828d`) are named according to the instructions on ELMS. Password for the user is `password`.
3. Run `python server.py` from the command line
4. Navigate to `localhost:8000` in the browser (I tested in Google Chrome)

# Navigating the Interface

My dashboard presents NBA player historical data in 3 different widgets. In basketball, players contribute to the success of their team by performing useful actions, which when successful are recorded as points, rebounds, assists, steals, or blocks. Players perform these actions during game time, which is measured in minutes.

My primary visualization, a **stacked area chart**, allows the visualization, for a selected statstic from the afformentioned 6, of the sum of the values recorded, per year/season, sorted by player position. Each position, point guard (PG), shooting guard (SG), small forward (SF), power forward (PF), and center (C), has a distinct color that represents it in all 3 visualizations. For the main visualization, when a **position's component (either name or color dot) is hovered in the legend**, the areas for the other positions are made transparent.

I have two secondary visualizations. The one on the bottom left, a **bar chart**, shows how many times each position had a player lead the league in the chosen statistical category for a season/year. The one on the bottom right, a **line chart**, shows the average height of players at each position. Notice that the y axis starts at 72 inches.

For the area and bar charts, **selecting a different attribute from the row of buttons** at the top changes the information displayed to correspond to the second attribute.

For all charts, **brushing an area (click and drag box) on the primary visualization** selects a time window that then is used to filter for all 3 visualizations.

The **RESET button** resets the time range. It does not change the backend. This was to address a deduction from my A2. There are also now titles for the y axes, to address the other deduction.

There are **backend buttons** at the top to toggle between backends. A3 is the default.

# User Study

Please take the survey at the following link. It will also walk you throught the study. All questions are meant to be answered with no prior knowledge about basketball or the visualization beyond the statements in "Navigating the Interface."

https://docs.google.com/forms/d/e/1FAIpQLScNftK45CGiCXlFdU-NsgsBIYmVqfSxPt47dgk_LOLQIZtTDw/viewform?usp=sf_link
