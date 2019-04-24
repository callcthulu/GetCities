from geopy.geocoders import Nominatim
import pycountry as pc
import dbconnect as dbc
import re
import pandas as pd

"""Main purpose: get city name, get country name by OpenMaps
    Thinkgs done:
        1. Get data from fb or csv file
        2. Clean address a little bit
        3. Get raw address from OpenMaps
        4. Optimise string with address if city and country not find
        5. Get postal code
        6. Save data to file
    To-do:
        1. Get data from MSQL
        2. Get back data to MSQL
    Additional targets:
        1. Get longitude, latitude
        2. Use Bing service
        3. Save results to db dictionary [address, city, country, longitude, latitude]
"""

def getCountry (address):
    """Finding country in address"""
    addressWordList = address.upper().split(" ")
    for word in addressWordList[::-1]: #starting from the end, usualy name of coutry is one of the last elements of adress
        for country in pc.countries:
            if word == country.alpha_2.upper() or word == country.alpha_3.upper():
                return country.alpha_2
    for country in pc.countries:
        if set(country.name.upper().split(" ")).issubset(addressWordList):
            return country.alpha_2
    return None


def getPostalCode (address):
    """Finding postal code in address"""
    address = address.split(" ")
    postalCode = ""
    for word in address[::-1]:
        # the postal code or fragment of postal code has at least one digit and is longer than two characters
        if len(word) > 2 and re.match(r"\d", word):
            postalCode += " " + word #british postal codes have space between
        if len(postalCode) > 3: #to avoid concatenating home number hopefully
            break
    if len(postalCode) > 0:
        return postalCode.strip()
    else:
        return None

def getCity (address):
    """Finding city in address"""
    city = ""
    postalCode = getPostalCode(address)
    if postalCode:
        address = address.split(postalCode)
        for word in address[1].split(" ")[::-1]:
            if not word.isdigit() and word not in [country.alpha_2 for country in pc.countries]:
                city = word +" "+city
        return city.lstrip().rstrip()
    else:
        for i, word in enumerate(address.split(" ")[::-1]):
            if not word.isdigit() and word.lower() not in [country.alpha_2.lower() for country in pc.countries]:
                city = word +""+city
            if i == 3:
                return city.lstrip().rstrip()

def geoDataFromBing(address):
    """TO-DO if needed"""
    pass

def getCityFromNominatim(dic):
    """get city from OpenMaps"""
    if "village" in dic:
        return dic.get("village")
    elif "city" in dic:
        return dic.get("city")
    elif "county" in dic:
        return dic.get("county")
    else: return None

###Geolocator tests
def geoDataFromAddress(address):
    geolocator = Nominatim(user_agent="Tax_DA_test")
    location = geolocator.geocode(address, addressdetails = True)
    if location:
        return [location.raw.get("address").get("country_code"), getCityFromNominatim(location.raw.get("address"))]
    else:
        shortAddress = "".join([getCity(address)," ",getCountry(address)])
        location = geolocator.geocode(shortAddress, addressdetails = True)
        if location:
            return [location.raw.get("address").get("country_code"), getCityFromNominatim(location.raw.get("address"))]
    return [None, None]

###Clear addresses
def clearAddress(address):
    words = address.strip().split(" ")
    address = ""
    for word in words:
        address += word[0].upper() + word[1:].lower() + str(" ")
    return address


#Main program
#Input: invoice, fullAdress
    #DBConnector:
#addressList = dbc.dbConnect("C:\Users\oleli\Desktop\DA DT materiały\connectionString.txt","SELECT TOP 3 NumerFaktury, AdresKontrahentaJPK_FA FROM da.JPK_FA_VAT;").getData()
#addressDF = pd.DataFrame(addressList, columns=["doc","address"])
    #FileConnector:
#addressDF = pd.read_csv("test.txt",sep=",", index_col=0, header=0)
    #PandasConnector:
data = [["6002976","Ul. Wincentego Pola 1 31-532 Kraków Pl"]]
addressDF = pd.DataFrame(data, columns=["doc","address"])
addressDF["address"] = addressDF["address"].apply(clearAddress)
addressDF["country"], addressDF["city"] = zip(*addressDF["address"].apply(geoDataFromAddress))
addressDF["postalCode"] = addressDF["address"].apply(getPostalCode)
#Output: invoiceNo, fullAdress, country, city, postalCode
    #OutputToFile:
#addressDF.to_csv("test.txt", sep=",")
print(addressDF)
