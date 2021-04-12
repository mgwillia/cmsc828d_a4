import csv

height_map = {}
with open('player_data.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        height_str = row['height']
        if height_str != '':
            print(height_str)
            feet, inches = height_str.split('-')
            height = int(feet) * 12 + int(inches)
            height_map[row['name']] = str(height)

new_rows = []
with open('Seasons_Stats.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Player'] != '':
            if int(row['Year']) >= 1982: ## 1982 is the last major stats began to be recorded
                if int(row['G']) >= 58: ## 58 is minimum games for a lot of awards and statistical titles
                    pts = row['PTS']
                    trb = row['TRB']
                    ast = row['AST']
                    stl = row['STL']
                    blk = row['BLK']
                    mp = row['MP']
                    name = row['Player'].replace('*', '')
                    position = row['Pos']
                    if '-' in position:
                        position = position.split('-')[0]

                    if name in height_map:
                        new_row = [row['Year'], name, position, row['Age'], row['Tm'], pts, trb, ast, stl, blk, mp, height_map[name]]
                        new_rows.append(new_row)

with open('nba_player_seasons.csv', 'w') as csvfile:
    csvfile.write('yr,player,pos,age,team,points,rebounds,assists,steals,blocks,minutes,height\n')
    for row in new_rows:
        csvfile.write(','.join(row) + '\n')

with open('sql_prep_file.txt', 'w') as textFile:
    for row in new_rows:
        #textFile.write('INSERT INTO nba_player_seasons(yr,player,pos,age,team,points,rebounds,assists,steals,blocks,minutes,height) VALUES (\"' + '\",\"'.join(row) + '\");\n')
        textFile.write('INSERT INTO nba_player_seasons(yr,player,pos,age,team,points,rebounds,assists,steals,blocks,minutes,height) VALUES (')
        textFile.write(row[0])
        textFile.write(',\'')
        textFile.write(row[1].replace('\'', ''))
        textFile.write('\',\'')
        textFile.write(row[2])
        textFile.write('\',')
        textFile.write(row[3])
        textFile.write(',\'')
        textFile.write(row[4])
        textFile.write('\',')
        textFile.write(row[5])
        textFile.write(',')
        textFile.write(row[6])
        textFile.write(',')
        textFile.write(row[7])
        textFile.write(',')
        textFile.write(row[8])
        textFile.write(',')
        textFile.write(row[9])
        textFile.write(',')
        textFile.write(row[10])
        textFile.write(',')
        textFile.write(row[11])
        textFile.write(');\n')