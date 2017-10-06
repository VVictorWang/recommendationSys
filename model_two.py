from scipy.sparse import coo_matrix
import numpy as np
from lightfm import LightFM


def get_data():
    file_path = 'data/behavior_info.txt'

    data, row, col = [], [], []
    items, users = {}, {}

    with open(file_path) as data_file:
        for n, line in enumerate(data_file):
            # If you use the original data from lastfm (14 million lines)
            # if n == SOMEINT: break

            # Readable data (for humans)
            readable_data = line.split('\t')
            user = readable_data[0]
            item_id = readable_data[1]
            # artist_name = readable_data[2]
            deeds = int(readable_data[3])

            if user not in users:
                users[user] = len(users)

            if item_id not in items:
                items[item_id] = len(items)

            data.append(deeds)
            row.append(users[user])
            col.append(items[item_id])

    coo = coo_matrix((data, (row, col)))

    dictionary = {
        'matrix': coo,
        'items': items,
        'users': len(users)
    }
    return dictionary


def get_my_data(file_path):
    my_result = []
    with open(file_path) as data_file:
        for n, line in enumerate(data_file):
            readable_data = line.split('\t')
            my_result.append(int(readable_data[0]))

    return my_result


def get_recommendataion(model, coo_mtrx, user_id):
    n_items = coo_mtrx.shape[1]
    result = []
    # Artists the model predicts they will like
    scores = model.predict(user_id, np.arange(n_items))
    top_scores = np.argsort(-scores)[:12]
    for x in top_scores.tolist():
        for i, value in data['items'].items():
            if int(x) == value:
                result.append(int(i))

    return result


print('getting data...')
data = get_data()
# items = get_my_data('data/product_info.txt')
users = get_my_data('data/user_info.txt')

print('fitting model...')
model = LightFM(loss='warp')
model.fit(data['matrix'], epochs=30, num_threads=4)
print('generating result...')
# result = []
count = 0
length = len(users)
f = open('data/result.txt', 'w')
for user in users:
    print('percentage: ', count, '/', length)
    count += 1
    recommends = get_recommendataion(model, data['matrix'], user)
    for i in recommends:
        f.write(str(user))
        f.write('\t')
        f.write(str(i))
        f.write('\n')
    # result.append([user, recommends])

# print('writting result...')
# with open('data/result.txt', 'w') as f:
#     for value in result:
#         recommend = value[1]
#         for i in recommend:
#             f.write(str(value[0]))
#             f.write('\t')
#             f.write(str(i))
#             f.write('\n')
