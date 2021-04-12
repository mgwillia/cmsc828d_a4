import psycopg2

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

#cursor.execute('DROP MATERIALIZED VIEW points_leaders;')
#cursor.execute('DROP MATERIALIZED VIEW rebounds_leaders;')
#cursor.execute('DROP MATERIALIZED VIEW assists_leaders;')
#cursor.execute('DROP MATERIALIZED VIEW steals_leaders;')
#cursor.execute('DROP MATERIALIZED VIEW blocks_leaders;')
#cursor.execute('DROP MATERIALIZED VIEW minutes_leaders;')
#cursor.execute('DROP MATERIALIZED VIEW height_stats;')
#conn.commit()

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