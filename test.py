import json
disco = '{"results":{"opensearch:Query":{"#text":"","role":"request","searchTerms":"Kirby Music","startPage":"1"},"opensearch:totalResults":"2","opensearch:startIndex":"0","opensearch:itemsPerPage":"50","albummatches":{"album":[{"name":"Bug Music: Music Of The Raymond Scott Quintette, John Kirby and His Orchestra, And The Duke Ellington Orchestra","artist":"Don Byron","id":"2815384","url":"http:\\/\\/www.last.fm\\/music\\/Don+Byron\\/Bug+Music:+Music+Of+The+Raymond+Scott+Quintette,+John+Kirby+and+His+Orchestra,+And+The+Duke+Ellington+Orchestra","image":[{"#text":"http:\\/\\/images.amazon.com\\/images\\/P\\/B000002I2Z.01._SCMZZZZZZZ_.jpg","size":"small"},{"#text":"http:\\/\\/images.amazon.com\\/images\\/P\\/B000002I2Z.01._SCMZZZZZZZ_.jpg","size":"medium"},{"#text":"http:\\/\\/images.amazon.com\\/images\\/P\\/B000002I2Z.01._SCMZZZZZZZ_.jpg","size":"large"},{"#text":"http:\\/\\/images.amazon.com\\/images\\/P\\/B000002I2Z.01._SCMZZZZZZZ_.jpg","size":"extralarge"}],"streamable":"0","mbid":""},{"name":"The Wonderful Jazz Music of Art Pepper, Chris Connors, John Kirby, Marty Paich and Other Hits, Vol. 2 (155 Songs)","artist":"Various Artists","id":"337505644","url":"http:\\/\\/www.last.fm\\/music\\/Various+Artists\\/The+Wonderful+Jazz+Music+of+Art+Pepper,+Chris+Connors,+John+Kirby,+Marty+Paich+and+Other+Hits,+Vol.+2+(155+Songs)","image":[{"#text":"http:\\/\\/userserve-ak.last.fm\\/serve\\/34s\\/91172411.jpg","size":"small"},{"#text":"http:\\/\\/userserve-ak.last.fm\\/serve\\/64s\\/91172411.jpg","size":"medium"},{"#text":"http:\\/\\/userserve-ak.last.fm\\/serve\\/126\\/91172411.jpg","size":"large"},{"#text":"http:\\/\\/userserve-ak.last.fm\\/serve\\/300x300\\/91172411.jpg","size":"extralarge"}],"streamable":"0","mbid":""}]},"@attr":{"for":"Kirby Music"}}}\n'
diccio = json.loads(disco)
diccio = diccio["results"]["albummatches"]["album"]
for elem in diccio:
	for el in elem.values():
		print el

print " --- "
diccio2 = json.loads(disco.encode('utf-8'))
diccio2 = diccio2["results"]["albummatches"]["album"]
for elem in diccio2:
	for el in elem.values():
 		print el
#print diccio
