from geopy.geocoders import Nominatim


def getData(query, adressDetails=True, additionalInfo=False, language='en', country_codes=None, exactlyOne=True, limit=1,
            inCoordinates=False, outRaw=False, outRawAdress=False, outAddress=True, outAltitude=False, outCoordinates=False):
    """get data from OpenMaps.
        Params:
        -> query - query build as expected by Nominatim (OpenMaps API), input: str, see more:
            https://nominatim.org/release-docs/develop/api/Search/
        -> addressDetails - if true break adress into elements , input: True/False
        -> additionalInfo - add non-address details like opening hours, wiki link etc., input: True/False
        -> nameDetails - add alternative names of object, e.g. in different language, input: True/False
        -> language - language of returned results, input: country name as in HTTP stantards
        -> country_codes - list of countries for which result will be searched, input: str or list, country as ISO 3166-1alpha2
        -> viewbox - box of preferred search where edge is coordinate, input: list, list of 2 tuples. E.g.: [Point(22, 180), Point(-22, -180)]
        -> bounded - only results from viewbox, input: True/False"""
    geolocator=Nominatim(user_agent="OLpy")
    if inCoordinates:
        location = geolocator.reverse(query,exactly_one=exactlyOne,language=language,addressdetails=adressDetails)
    else:
        location = geolocator.geocode(query, addressdetails=adressDetails, extratags=additionalInfo,
                                    language=language, country_codes=country_codes, limit=limit,
                                    viewbox=None, bounded=False, exactly_one=exactlyOne)
    returnSet = {}
    if outRaw:
        returnSet['raw'] = location.raw
    if outRawAdress:
        returnSet['rawAdress'] = location.raw['address']
    if outAddress:
        returnSet['address'] = location.address
    if outAltitude:
        returnSet['altitude'] = location.altitude
    if outCoordinates:
        returnSet['coordinates'] = (location.latitude,location.longitude)
    return list(returnSet.values())[0] if len(returnSet) == 1 else returnSet


def prepareQuery(country='', postalcode='', city='', street='', county='', state=''):
    """prepare dictionary for prepared query to OpenMaps API"""
    return locals()

def getAdressFromRaw(rawAdressDic,specificElements=None, asText=False):

    def getDetails(listOfKeys,dic=rawAdressDic):
        """get details from OpenMaps"""
        for key in listOfKeys:
            if key in dic:
                return dic.get(key)
        return None

    def getSpecificElements(elements,dic):
        """get only elemenets of adress specify in list"""
        if type(elements) != list:
            elements = [elements]
        specificSet = {}
        for element in elements:
            if element in dic:
                specificSet[element] = dic[element]
        return specificSet

    returnSet = {
        'house': getDetails(['house_number']),
        'street': getDetails(['street','road']),
        'neighbourhood': getDetails(['neighbourhood']),
        'suburb': getDetails(['suburb']),
        'cityDistrict': getDetails(['city_district']),
        'city': getDetails(['village','city','county']),
        'state': getDetails(['state']),
        'postCode': getDetails(['postcode']),
        'country': getDetails(['country']),
        'countryCode': getDetails(['country_code'])
    }

    if specificElements:
        returnSet = getSpecificElements(specificElements,returnSet)

    if asText:
        return [value for key, value in returnSet]

    return returnSet