#R1 stands for relation 1, which is the Audiobook_owns table
import mysql.connector


conn = mysql.connector.connect(
    host="localhost",       
    user="christa", 
    password="sdcn2024",
    database="global_music_db"  
)

cursor = conn.cursor()

insert_query = """
INSERT INTO Audiobook_Owns (audiobook_id, artist_id)
SELECT audiobook_id, artist_id
FROM Audiobooks
"""

cursor.execute(insert_query)


conn.commit()
print(f"{cursor.rowcount} rows inserted into Audiobook_Owns table.")

cursor.close()
conn.close()