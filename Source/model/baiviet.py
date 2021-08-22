import utils.database

TABLE_NAME = "baiviet"

def create_schema_bai_viet():
    global TABLE_NAME
    return f""" CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                                        website_id text PRIMARY KEY,
                                        website text not null,
                                        url text,
                                        full_name text not null,
                                        phone text,
                                        district text not null,
                                        rate real,
                                        rate_count integer,
                                        favorite integer,
                                        active_time text not null,
                                        price_from real,
                                        price_to real,
                                        other_service text
                                    ); """

def create_indexes_bai_viet():
    global TABLE_NAME

    def create_index_tmp(field):
        return f"CREATE INDEX IF NOT EXISTS {field}_index ON {TABLE_NAME} ({field});"
    
    return create_index_tmp("website")+create_index_tmp("district")+create_index_tmp("rate")+create_index_tmp("favorite")

def add_bai_viet(
    website_id_quan: str, 
    website: str,
    url: str,
    district: str,
    rate: float,
    active_time: str,
    full_name: str = None,
    phone: str = None,
    rate_count: float = None,
    favorite: float = None,
    price_from: float = None,
    price_to: float = None,
    other_service: str = None,
):
    global TABLE_NAME
    utils.database.insert_value(TABLE_NAME, [website_id_quan,website,url,full_name,phone,district,rate,
        rate_count,favorite,active_time,price_from,price_to,other_service])

def get_bai_viet():
    global TABLE_NAME
    listData = utils.database.fetch_value(f"select * from {TABLE_NAME}")
    return listData.fetchall()
