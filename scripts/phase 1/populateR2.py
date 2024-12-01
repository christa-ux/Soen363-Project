#R2 stands for relation 2, which is the Track_owns table
import mysql.connector


conn = mysql.connector.connect(
    host="localhost",       
    user="christa", 
    password="sdcn2024",
    database="global_music_db"  
)

cursor = conn.cursor()

insert_query = """
INSERT INTO Track_Owns (track_id, artist_id)
SELECT track_id, artist_id
FROM Tracks
"""

cursor.execute(insert_query)


conn.commit()
print(f"{cursor.rowcount} rows inserted into Track_Owns table.")

cursor.close()
conn.close()