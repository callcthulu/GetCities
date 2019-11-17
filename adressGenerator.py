"""
    Script to generate real random adresses based on some partial data.
    Current methods:
    -> generate address based on postal code and country
"""

import mapAPIConnect as mac
import codecs

maxBuffer = 1
buffer=  0
fromDB = [('pl','54-001'),('pl','03-890'),('pl','03-889')]
insert = ''
table = 'listOfPostals'
target = table+'.sql'

with codecs.open(target, 'w', 'utf-8') as file:
    file.write('CREATE TABLE '+table+' AS (house nvarchar(256), street nvarchar(256), city nvarchar(256), postalcode nvarchar(256), country nvarchar(256))')
"""take postalCode and City from DB postCode, country to memory"""
for country, postCode in fromDB:
    query2 = mac.prepareQuery(country,postCode)
    coordinates = mac.getData(query2,outAddress=False,outCoordinates=True)
    raw = mac.getData(coordinates,inCoordinates=True,outAddress=False,outRawAdress=True,language=country)
    address = mac.getAdressFromRaw(raw,['house','street','city'])
    address['postCode'] = postCode
    address['country'] = country
    insert += chr(13) + 'INSERT INTO ' + table + ' VALUES( \'' + '\', \''.join(value for value in list(address.values()))+'\');'
    buffer += 1
    print(insert)
    if buffer == maxBuffer:
        with codecs.open(target, 'a', 'utf-8') as file:
            file.write(insert)
        buffer = 0
        insert = ''
