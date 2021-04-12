try:
    import simplejson as json
except ImportError:
    import json
from flask import Flask,request,Response,render_template
import psycopg2
import time
app = Flask(__name__)

stacked_data_cache = {}
leader_position_cache = {}
height_data_cache = {}
year_to_index = {}

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

def getPositions(cursor):
  cursor.execute('SELECT DISTINCT pos FROM nba_player_seasons;')
  results = cursor.fetchall()
  attributes = []
  for result in results:
    attributes.append(result[0])
  return attributes

#############################
######## A2 Backend #########
#############################

def getHeightDataA2(cursor, min_year, max_year):
  cursor.execute('SELECT pos, yr, height FROM nba_player_seasons WHERE yr >= ' + min_year + ' AND yr <=' + max_year + ';')
  results = cursor.fetchall()

  max_height = 0.0

  pos_yr_val = {}
  for result in results:
    pos = result[0]
    if pos not in pos_yr_val:
      pos_yr_val[pos] = {}
    yr = int(result[1])
    if yr not in pos_yr_val[pos]:
      pos_yr_val[pos][yr] = {
        'height_sum': 0,
        'count': 0
      }
    val = result[2]
    pos_yr_val[pos][yr]['height_sum'] += val
    pos_yr_val[pos][yr]['count'] += 1

  height_data = [{'key': 'PG', 'values': []},{'key': 'SG', 'values': []},{'key': 'SF', 'values': []},{'key': 'PF', 'values': []},{'key': 'C', 'values': []}]
  start_yr = min(pos_yr_val['C'].keys())
  end_yr = max(pos_yr_val['C'].keys())
  for yr in range(start_yr, end_yr + 1):
    if yr == 1999:
      continue
    endVal = 0
    for i, pos in enumerate(['PG', 'SG', 'SF', 'PF', 'C']):
      avg_height = pos_yr_val[pos][yr]['height_sum'] / float(pos_yr_val[pos][yr]['count'])
      if avg_height > max_height:
        max_height = avg_height
      cur_data = {
        'pos': pos,
        'year': yr,
        'height': avg_height
      }
      height_data[i]['values'].append(cur_data)
  
  return height_data, max_height

def getLeaderPositionBucketsA2(cursor, cur_attr_name, min_year, max_year):
  cursor.execute('SELECT o.pos FROM nba_player_seasons o ' +
    'LEFT JOIN nba_player_seasons b ON o.yr = b.yr AND o.' + cur_attr_name + ' < b.' + cur_attr_name + ' WHERE b.' + cur_attr_name + ' is NULL AND o.yr >= ' + 
    min_year + ' AND o.yr <= ' + max_year + ';')
  results = cursor.fetchall()

  leader_position_buckets = {}
  for result in results:
    pos = result[0]
    if pos not in leader_position_buckets:
      leader_position_buckets[pos] = 0
    leader_position_buckets[pos] += 1
  
  for key in ['PG', 'SG', 'SF', 'PF', 'C']:
    if key not in leader_position_buckets:
      leader_position_buckets[key] = 0

  return leader_position_buckets

def getStackedDataA2(cursor, cur_attr_name, min_year, max_year):
  cursor.execute('SELECT pos, yr, ' + cur_attr_name + ' FROM nba_player_seasons WHERE yr >= ' + str(min_year) + ' AND yr <= ' + str(max_year) + ';')
  results = cursor.fetchall()

  pos_yr_val = {}
  for result in results:
    pos = result[0]
    if pos not in pos_yr_val:
      pos_yr_val[pos] = {}
    yr = int(result[1])
    if yr not in pos_yr_val[pos]:
      pos_yr_val[pos][yr] = 0
    val = result[2]
    pos_yr_val[pos][yr] += val

  stacked_values = [[],[],[],[],[]]
  stacked_data = [[],[],[],[],[]]
  start_yr = min(pos_yr_val['C'].keys())
  end_yr = max(pos_yr_val['C'].keys())
  for yr in range(start_yr, end_yr + 1):
    if yr == 1999:
      continue
    endVal = 0
    for i, pos in enumerate(['PG', 'SG', 'SF', 'PF', 'C']):
      startVal = endVal
      endVal += pos_yr_val[pos][yr]
      cur_data = {
        'values': [startVal, endVal],
        'year': yr,
        'key': pos
      }
      stacked_values[i].append([startVal, endVal])
      stacked_data[i].append(cur_data)

  return stacked_values, stacked_data

#############################
######## A3 Backend #########
#############################

def initYearToIndex():
  i = 0
  for yr in range(1982, 2018):
    if yr != 1999:
      year_to_index[yr] = i
      i += 1

def getCachedStackedData(cursor, cur_attr_name):
  if cur_attr_name not in stacked_data_cache:
    cursor.execute('SELECT pos, yr, SUM(' + cur_attr_name + ')::NUMERIC(10) FROM nba_player_seasons GROUP BY pos, yr;')
    results = cursor.fetchall()

    pos_yr_val = {}
    for result in results:
      pos = result[0]
      if pos not in pos_yr_val:
        pos_yr_val[pos] = {}
      yr = int(result[1])
      if yr not in pos_yr_val[pos]:
        pos_yr_val[pos][yr] = 0
      val = int(result[2])
      pos_yr_val[pos][yr] = val

    stacked_values = [[],[],[],[],[]]
    stacked_data = [[],[],[],[],[]]
    start_yr = min(pos_yr_val['C'].keys())
    end_yr = max(pos_yr_val['C'].keys())
    for yr in range(start_yr, end_yr + 1):
      if yr == 1999:
        continue
      endVal = 0
      for i, pos in enumerate(['PG', 'SG', 'SF', 'PF', 'C']):
        startVal = endVal
        endVal += pos_yr_val[pos][yr]
        cur_data = {
          'values': [startVal, endVal],
          'year': yr,
          'key': pos
        }
        stacked_values[i].append([startVal, endVal])
        stacked_data[i].append(cur_data)

    stacked_data_cache[cur_attr_name] = stacked_values, stacked_data
  
  return stacked_data_cache[cur_attr_name]

def getCachedLeaderPositionBuckets(cursor, cur_attr_name):
  if cur_attr_name not in leader_position_cache:
    cursor.execute('SELECT * from ' + cur_attr_name + '_leaders;')
    results = cursor.fetchall()
    leader_position_cache[cur_attr_name] = results
  return leader_position_cache[cur_attr_name]

def getCachedHeightData(cursor):
  if 'height_data' not in height_data_cache:
    cursor.execute('SELECT * FROM height_stats;')
    results = cursor.fetchall()

    max_height = 0.0

    pos_yr_val = {}
    for result in results:
      pos = result[0]
      if pos not in pos_yr_val:
        pos_yr_val[pos] = {}
      yr = int(result[1])
      if yr not in pos_yr_val[pos]:
        pos_yr_val[pos][yr] = {
          'height_sum': 0,
          'count': 0
        }
      val = result[2]
      pos_yr_val[pos][yr] = float(val)

    height_data = [{'key': 'PG', 'values': []},{'key': 'SG', 'values': []},{'key': 'SF', 'values': []},{'key': 'PF', 'values': []},{'key': 'C', 'values': []}]
    start_yr = min(pos_yr_val['C'].keys())
    end_yr = max(pos_yr_val['C'].keys())
    for yr in range(start_yr, end_yr + 1):
      if yr == 1999:
        continue
      endVal = 0
      for i, pos in enumerate(['PG', 'SG', 'SF', 'PF', 'C']):
        avg_height = pos_yr_val[pos][yr]
        if avg_height > max_height:
          max_height = avg_height
        cur_data = {
          'pos': pos,
          'year': yr,
          'height': avg_height
        }
        height_data[i]['values'].append(cur_data)
  
    height_data_cache['height_data'] = height_data, max_height
  return height_data_cache['height_data']

def getHeightData(cursor, min_year, max_year):
  height_data, max_height = getCachedHeightData(cursor)
  start_index = year_to_index[int(min_year)]
  end_index = year_to_index[int(max_year)]
  filtered_height_data = [{'key': 'PG', 'values': []},{'key': 'SG', 'values': []},{'key': 'SF', 'values': []},{'key': 'PF', 'values': []},{'key': 'C', 'values': []}]
  for i in range(5):
    filtered_height_data[i]['values'] = height_data[i]['values'][start_index:end_index+1]
  return filtered_height_data, max_height

def getLeaderPositionBuckets(cursor, cur_attr_name, min_year, max_year):
  leaderPositionResults = getCachedLeaderPositionBuckets(cursor, cur_attr_name)

  leader_position_buckets = {}
  years = []
  for result in leaderPositionResults:
    pos = result[0]
    yr = result[1]
    if pos not in leader_position_buckets:
      leader_position_buckets[pos] = 0
    if yr not in years and yr >= int(min_year) and yr <= int(max_year):
      years.append(yr)
      leader_position_buckets[pos] += 1
  
  for key in ['PG', 'SG', 'SF', 'PF', 'C']:
    if key not in leader_position_buckets:
      leader_position_buckets[key] = 0

  return leader_position_buckets

def getStackedData(cursor, cur_attr_name, min_year, max_year):
  stacked_values, stacked_data = getCachedStackedData(cursor, cur_attr_name)
  start_index = year_to_index[int(min_year)]
  end_index = year_to_index[int(max_year)]
  new_stacked_values = [[],[],[],[],[]]
  new_stacked_data = [[],[],[],[],[]]
  for i in range(5):
    new_stacked_values[i] = stacked_values[i][start_index:end_index+1]
    new_stacked_data[i] = stacked_data[i][start_index:end_index+1]
  return new_stacked_values, new_stacked_data

###### ROUTES ######

@app.route('/get-data')
def getData():
  backend_version = request.args.get('backend')
  cur_attr_name = request.args.get('attribute')
  min_year = str(request.args.get('min'))
  max_year = str(request.args.get('max'))
  initYearToIndex()

  cursor, conn = getCursor()

  try:
    if backend_version == 'A3':
      start_time = time.time()
      stacked_values, stacked_data = getStackedData(cursor, cur_attr_name, min_year, max_year)
      leader_position_buckets = getLeaderPositionBuckets(cursor, cur_attr_name, min_year, max_year)
      height_data, max_height = getHeightData(cursor, min_year, max_year)
      end_time = time.time()
      print('Data retrieval and processing took {} seconds!'.format(end_time - start_time))
    else:
      start_time = time.time()
      stacked_values, stacked_data = getStackedDataA2(cursor, cur_attr_name, min_year, max_year)
      leader_position_buckets = getLeaderPositionBucketsA2(cursor, cur_attr_name, min_year, max_year)
      height_data, max_height = getHeightDataA2(cursor, min_year, max_year)
      end_time = time.time()
      print('Data retrieval and processing took {} seconds!'.format(end_time - start_time))

    conn.close()

    aggregate_data = {}
    aggregate_data['attributes'] = ['points', 'rebounds', 'assists', 'steals', 'blocks', 'minutes']
    aggregate_data['leader_position_buckets'] = leader_position_buckets
    aggregate_data['stacked_values'] = stacked_values
    aggregate_data['stacked_data'] = stacked_data
    aggregate_data['height_data'] = height_data
    aggregate_data['max_height'] = max_height

    resp = Response(response=json.dumps(aggregate_data),status=200,mimetype='application/json')
    h = resp.headers
    h['Access-Control-Allow-Origin'] = "*"
    return resp
  except Exception as err:
    raise err

@app.route('/')
def renderPage():
  return render_template("index.html")


if __name__ == "__main__":
  app.run(debug=True,port=8000)
