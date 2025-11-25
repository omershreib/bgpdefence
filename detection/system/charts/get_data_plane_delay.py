def get_data_plane_delay(data_plane):
    # todo: handle case of empty hops array
    for hop in data_plane['hops'][::-1]:
        if hop['responded']:
            return min([delay for delay in hop['delays'] if delay is not None])

    return 0


if __name__ == '__main__':
    from pymongo import MongoClient
    from bson.objectid import ObjectId


    client = MongoClient("mongodb://localhost:27017/")
    db = client["network_monitoring"]
    collection = db["traceroutes"]

    delay_data = []

    mongo_filter = {
        'sensor_id': 1
    }
    sort = list({'timestamp': -1}.items())
    limit = 3
    mongo_delay_temp = collection.find(
        filter=mongo_filter,
        sort=sort,
        limit=limit
    )

    for item in mongo_delay_temp:
        print(item['timestamp'].strftime("%H:%M:%S"), get_data_plane_delay(item))

    #data_plane = collection.find_one({"_id": ObjectId("691dc51910d50060d21782a4")})
    #print(get_data_plane_delay(data_plane))