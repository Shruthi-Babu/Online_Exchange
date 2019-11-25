import sqlite3

conn = sqlite3.connect('olx.db')
c = conn.cursor()

def category_table():

    c.execute('''CREATE TABLE IF NOT EXISTS CATEGORY
              (
              CAT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
              CATEGORY_NAME varchar(10),
              logo varchar(100)              
              ); ''')
    c.execute('''insert into CATEGORY(CATEGORY_NAME, LOGO) values('Laptops','/static/laptop.jpeg');''')
    c.execute('''insert into CATEGORY(CATEGORY_NAME, LOGO) values('Mobiles','/static/mobile.jpeg');''')
    c.execute('''insert into CATEGORY(CATEGORY_NAME, LOGO) values('Furniture','/static/furniture.jpeg');''')



def user_table():
    c.execute('''CREATE TABLE IF NOT EXISTS USERS
         (
         USER_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         NAME   VARCHAR(20)    NOT NULL,
         EMAIL  VARCHAR(20)    NOT NULL,
         PHONE INTEGER(10) NOT NULL,
         PASSWORD   VARCHAR(20)    NOT NULL
         );''')

    c.execute('''insert into USERS(NAME, EMAIL, PHONE, PASSWORD) values('Sansa','sansa@gmail.com','12345','sansa');''')
    c.execute('''insert into USERS(NAME, EMAIL, PHONE, PASSWORD) values('Rob','rob@gmail.com','14545','rob');''')
    c.execute('''insert into USERS(NAME, EMAIL, PHONE, PASSWORD) values('Jon','jon@gmail.com','12376','jon');''')




def items_table():
    c.execute('''CREATE TABLE IF NOT EXISTS ITEMS2
    (
    ITEM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    NAME varchar(50) ,
    CAT_ID INTEGER,    
    PRICE integer,
    HOW_OLD INTEGER,
    OWNER_ID INTEGER,
    PICTURE VARCHAR(50),
    constraint fkm1 foreign key(CAT_ID) references CATEGORY(CAT_ID) on delete cascade,
    constraint fkm2 foreign key(OWNER_ID) references USERS(USER_ID) on delete cascade    ); ''')

    c.execute('''insert into ITEMS2(NAME, CAT_ID, PRICE,HOW_OLD, OWNER_ID, PICTURE) values('2 seater sofa',3, 5000,2,1,'/static/2seater.jpeg');''')
    c.execute('''insert into ITEMS2(NAME, CAT_ID, PRICE,HOW_OLD, OWNER_ID, PICTURE) values('iphone X',2, 55000,6,3,'/static/iphonex.jpeg');''')
    c.execute('''insert into ITEMS2(NAME, CAT_ID, PRICE,HOW_OLD, OWNER_ID, PICTURE) values('Lenovo',1, 25000,7,2,'/static/lenovo.jpeg');''')


def order_table():
    c.execute('''CREATE TABLE IF NOT EXISTS ORDERS
    (
    ORDER_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    OWNER_ID INTEGER NOT NULL,
    BUYER_ID INTEGER NOT NULL,
    ITEM_ID INTEGER NOT NULL,
    ORD_DATE VARCHAR(10),
    COST INTEGER,
    constraint fk_or1 foreign key(OWNER_ID) references USERS(USER_ID) on delete cascade,
    constraint fk_or1 foreign key(BUYER_ID) references USERS(USER_ID) on delete cascade,
    constraint fk_or2 foreign key(ITEM_ID) references ITEMS(ITEM_ID) on delete cascade
    ); ''')



# category_table()
# user_table()
# items_table()
# order_table()

def drop():
    c.execute('''drop table category''')
    c.execute('''drop table items2''')
    c.execute('''drop table orders''')
    c.execute('''drop table users''')


#drop()


def insert():
    c.execute('''insert into CATEGORY(CATEGORY_NAME, LOGO) values('Vehicles','/static/vehicles.png');''')
    c.execute('''insert into ITEMS2(NAME, CAT_ID, PRICE,HOW_OLD, OWNER_ID, PICTURE) values('Swift Dzire',4, 250000,3,2,'/static/dzire.jpeg');''')
    c.execute('''insert into ITEMS2(NAME, CAT_ID, PRICE,HOW_OLD, OWNER_ID, PICTURE) values('Hyundai i20',4, 35000,7,1,'/static/i20.jpeg');''')

insert()
conn.commit()
c.close()








