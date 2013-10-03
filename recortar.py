import csv
fp = open('sentiment.csv', 'rb')
reader = csv.reader(fp, delimiter=',', quotechar='"', escapechar='\\')

tweets = []
contador = 0
for row in reader:
    tweets.append((row[2], row[1], row[4]))

fp.close()
fp = open('sentiment2.csv', 'wb')
writer = csv.writer(fp, delimiter=',', quotechar='"', escapechar='\\', quoting=1)
for row in tweets:
    writer.writerow(row)

fp.close()
