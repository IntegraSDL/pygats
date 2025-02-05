import recog as rec
query = "./tests/find/background/query.jpg"
train = "./tests/find/background/train.jpg"
rec.image_comparison(query,train)