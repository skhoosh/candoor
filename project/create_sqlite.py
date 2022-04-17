import sqlite3

conn = sqlite3.connect('db.sqlite')
c = conn.cursor()

c.execute(
    '''
    CREATE TABLE "user" 
    ( `id` INTEGER NOT NULL, 
    `email` VARCHAR ( 100 ) UNIQUE, 
    `password` VARCHAR ( 100 ), 
    `name` VARCHAR ( 1000 ), 
    `tg_id` TEXT, 
    PRIMARY KEY(`id`) )
    '''
)
conn.commit()
conn.close()