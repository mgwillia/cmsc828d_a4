import psycopg2
import random
from statistics import mean
import csv
import sys
import time

###### HELPERS ######

def getCursor():
    conn = psycopg2.connect(
        host="localhost",
        database="a3database",
        port=5432,
        user="cmsc828d",
        password="password")
    cursor = conn.cursor()
    return cursor, conn

cursor, conn = getCursor()
try:
    cursor.execute('DROP MATERIALIZED VIEW points_leaders;')
    cursor.execute('DROP MATERIALIZED VIEW rebounds_leaders;')
    cursor.execute('DROP MATERIALIZED VIEW assists_leaders;')
    cursor.execute('DROP MATERIALIZED VIEW steals_leaders;')
    cursor.execute('DROP MATERIALIZED VIEW blocks_leaders;')
    cursor.execute('DROP MATERIALIZED VIEW minutes_leaders;')
    cursor.execute('DROP MATERIALIZED VIEW height_stats;')
    cursor.execute('DROP TABLE "nba_player_seasons";')
except Exception as e:
    print('creating table...')
conn.commit()
cursor.execute(
    'CREATE TABLE "nba_player_seasons" \
    ( \
        "age" smallint NOT NULL, \
        "assists" smallint NOT NULL, \
        "player" character varying NOT NULL, \
        "points" smallint NOT NULL, \
        "pos" character varying NOT NULL, \
        "rebounds" smallint NOT NULL, \
        "team" character varying NOT NULL, \
        "yr" smallint NOT NULL, \
        "blocks" smallint NOT NULL, \
        "steals" smallint NOT NULL, \
        "height" smallint NOT NULL, \
        "minutes" integer NOT NULL, \
        "id" serial NOT NULL, \
        PRIMARY KEY (id) \
    );'
)
conn.commit()

height_map = {}
with open('player_data.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        height_str = row['height']
        if height_str != '':
            feet, inches = height_str.split('-')
            height = int(feet) * 12 + int(inches)
            height_map[row['name']] = str(height)

#new_rows = []
years = []
positions = []
ages = []
teams = []
heightsDict = {}
ptsDict = {}
trbDict = {}
astDict = {}
stlDict = {}
blkDict = {}
mpDict = {}
with open('Seasons_Stats.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Player'] != '':
            if int(row['Year']) >= 1982: ## 1982 is the last major stats began to be recorded
                if int(row['G']) >= 58: ## 58 is minimum games for a lot of awards and statistical titles
                    pts = int(row['PTS'])
                    trb = int(row['TRB'])
                    ast = int(row['AST'])
                    stl = int(row['STL'])
                    blk = int(row['BLK'])
                    mp = int(row['MP'])
                    yr = row['Year']
                    name = row['Player'].replace('*', '')
                    position = row['Pos']
                    if '-' in position:
                        position = position.split('-')[0]

                    if position not in heightsDict:
                        heightsDict[position] = {}
                        ptsDict[position] = {}
                        trbDict[position] = {}
                        astDict[position] = {}
                        stlDict[position] = {}
                        blkDict[position] = {}
                        mpDict[position] = {}

                    if yr not in heightsDict[position]:      
                        heightsDict[position][yr] = []
                        ptsDict[position][yr] = []
                        trbDict[position][yr] = []
                        astDict[position][yr] = []
                        stlDict[position][yr] = []
                        blkDict[position][yr] = []
                        mpDict[position][yr] = []

                    if name in height_map:
                        #new_row = [yr, name, position, row['Age'], row['Tm'], pts, trb, ast, stl, blk, mp, height_map[name]]
                        #new_rows.append(new_row)

                        years.append(yr)
                        positions.append(position)
                        ages.append(row['Age'])
                        teams.append(row['Tm'])
                        heightsDict[position][yr].append(height_map[name])
                        ptsDict[position][yr].append(pts)
                        trbDict[position][yr].append(trb)
                        astDict[position][yr].append(ast)
                        stlDict[position][yr].append(stl)
                        blkDict[position][yr].append(blk)
                        mpDict[position][yr].append(mp)

#for row in new_rows:
#    cursor.execute('INSERT INTO nba_player_seasons(yr,player,pos,age,team,points,rebounds,assists,steals,blocks,minutes,height) VALUES ({}, \'{}\', \'{}\', {}, \'{}\', {}, {}, {}, {}, {}, {}, {})'.format(
#        row[0], row[1].replace('\'', ''), row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))
#    conn.commit()

rowsToGen = int(sys.argv[1])
numUniqueTuples = min(100000,rowsToGen)
print('For the sake of speed, only generating {} UNIQUE tuples'.format(numUniqueTuples))

startTime = time.time()
tuples = []
for i in range(numUniqueTuples):
    year = str(random.choice(years))
    name = 'rand' + str(i)
    position = str(random.choice(positions))
    age = str(random.choice(ages))
    team = str(random.choice(teams))

    randFactors = random.choices([-3, -2, -1, 0, 1, 2, 3], weights=[0.05, 0.1, 0.15, 0.4, 0.15, 0.1, 0.05], k=6)

    height = str(random.choice(heightsDict[position][year]))
    points = str(random.choice(ptsDict[position][year]) + int(randFactors[0] * mean(ptsDict[position][year]) / 82))
    rebounds = str(random.choice(trbDict[position][year]) + int(randFactors[1] * mean(trbDict[position][year]) / 82))
    assists = str(random.choice(astDict[position][year]) + int(randFactors[2] * mean(astDict[position][year]) / 82))
    steals = str(random.choice(stlDict[position][year]) + int(randFactors[3] * mean(stlDict[position][year]) / 82))
    blocks = str(random.choice(blkDict[position][year]) + int(randFactors[4] * mean(blkDict[position][year]) / 82))
    minutes = str(random.choice(mpDict[position][year]) + int(randFactors[5] * mean(mpDict[position][year]) / 82))

    tuples.append((year, name, position, age, team, points, rebounds, assists, steals, blocks, minutes, height))
endTime = time.time()

print('Data generated in ' + str(endTime - startTime) + ' seconds, uploading to database now.')

numFullBatches = int(rowsToGen // numUniqueTuples)
print('Uploading {} full batches of {} unique tuples'.format(numFullBatches, numUniqueTuples))
for i in range(numFullBatches):
    args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", x).decode("utf-8") for x in tuples)
    cursor.execute("INSERT INTO nba_player_seasons(yr,player,pos,age,team,points,rebounds,assists,steals,blocks,minutes,height) VALUES " + args_str) 
    conn.commit()
    print('Successfully uploaded batch {}'.format(i + 1))

numTuplesRemaining = rowsToGen - (numUniqueTuples * numFullBatches)
if numTuplesRemaining > 0:
    print('Uploading {} remaining tuples'.format(numTuplesRemaining))
    args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", x).decode("utf-8") for x in tuples[:numTuplesRemaining])
    cursor.execute("INSERT INTO nba_player_seasons(yr,player,pos,age,team,points,rebounds,assists,steals,blocks,minutes,height) VALUES " + args_str) 
    conn.commit()


###############################
## CREATE MATERIALIZED VIEWS ##
###############################
cursor.execute(
    'CREATE MATERIALIZED VIEW points_leaders \
    AS \
    SELECT o.pos, o.yr FROM nba_player_seasons o \
    LEFT JOIN nba_player_seasons b ON o.yr = b.yr AND o.points < b.points WHERE b.points is NULL;'
)
conn.commit()

cursor.execute(
    'CREATE MATERIALIZED VIEW rebounds_leaders \
    AS \
    SELECT o.pos, o.yr FROM nba_player_seasons o \
    LEFT JOIN nba_player_seasons b ON o.yr = b.yr AND o.rebounds < b.rebounds WHERE b.rebounds is NULL;'
)
conn.commit()

cursor.execute(
    'CREATE MATERIALIZED VIEW assists_leaders \
    AS \
    SELECT o.pos, o.yr FROM nba_player_seasons o \
    LEFT JOIN nba_player_seasons b ON o.yr = b.yr AND o.assists < b.assists WHERE b.assists is NULL;'
)
conn.commit()

cursor.execute(
    'CREATE MATERIALIZED VIEW steals_leaders \
    AS \
    SELECT o.pos, o.yr FROM nba_player_seasons o \
    LEFT JOIN nba_player_seasons b ON o.yr = b.yr AND o.steals < b.steals WHERE b.steals is NULL;'
)
conn.commit()

cursor.execute(
    'CREATE MATERIALIZED VIEW blocks_leaders \
    AS \
    SELECT o.pos, o.yr FROM nba_player_seasons o \
    LEFT JOIN nba_player_seasons b ON o.yr = b.yr AND o.blocks < b.blocks WHERE b.blocks is NULL;'
)
conn.commit()

cursor.execute(
    'CREATE MATERIALIZED VIEW minutes_leaders \
    AS \
    SELECT o.pos, o.yr FROM nba_player_seasons o \
    LEFT JOIN nba_player_seasons b ON o.yr = b.yr AND o.minutes < b.minutes WHERE b.minutes is NULL;'
)
conn.commit()

cursor.execute(
    'CREATE MATERIALIZED VIEW height_stats \
    AS \
    SELECT pos, yr, avg(height)::NUMERIC(10,2) FROM nba_player_seasons GROUP BY pos, yr;'
)
conn.commit()

conn.close()

print('Finished!')
