USE [825c2c4a-2c33-4df6-89ee-4cb8dd294a00]
GO
/****** Object:  StoredProcedure [da].[PythonTests]    Script Date: 02.07.2019 13:35:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER PROCEDURE [da].[PythonTests] 
 @tableName nvarchar(256)
,@columnName nvarchar(256)
,@schemaName nvarchar(256)
,@targetTableName nvarchar(256)
,@iftest bit = 0
,@rowno  int = NULL
AS
	--set table
		SET NOCOUNT ON;

	--used variables:
		DECLARE @InputDataQuery		nvarchar(4000)  
		DECLARE @AddressTaken		int
		DECLARE @AddressesToCheck	int
		DECLARE @AddressesInserted	int
		;
	
	--getting addresses
	CREATE TABLE #AddressList ( address nvarchar(1024) )

	SET @InputDataQuery = N'SELECT DISTINCT '+@columnName+'
							FROM '+@schemaName+'.'+@tableName+'
							WHERE '+@columnName+' IS NOT NULL AND LEN('+@columnName+') != 0'
	;
	--PRINT @InputDataQuery;
	INSERT INTO #AddressList
	EXECUTE sp_executeSQL @InputDataQuery;
	SET @AddressTaken = @@ROWCOUNT;
	
	--check if address was already checked and target table exisits
	IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'da' AND TABLE_NAME = @targetTableName)
		BEGIN
			SET @InputDataQuery = 'CREATE TABLE '+@schemaName+'.'+@targetTableName+' ( rawAddress nvarchar(1024) PRIMARY KEY, clearAddress nvarchar(1024), country nvarchar(8), city nvarchar(256), postalcode nvarchar(32), timestamp datetime )'
			;
			PRINT @InputDataQuery;
			EXECUTE sp_executeSQL @InputDataQuery;
		END

	SET @InputDataQuery = N'DELETE FROM #AddressList WHERE address IN (SELECT DISTINCT rawAddress FROM '+@schemaName+'.'+@targetTableName+')'
	;
	EXECUTE sp_executeSQL @InputDataQuery;
	SET @AddressesToCheck = @AddressTaken - @@ROWCOUNT;

	IF @iftest = 1
	BEGIN
		IF @rowno IS NULL
			BEGIN
				SET @rowno = @AddressesToCheck
			END
		SET @InputDataQuery = N'DELETE FROM #AddressList WHERE address NOT IN (SELECT TOP '+CAST(@rowno AS nvarchar(256))+' address FROM #AddressList)'
		;
		EXECUTE sp_executeSQL @InputDataQuery;
	END
	
	--send addresses to check them and get cities / countries
		CREATE TABLE #Responses
		(
		  rawAddress nvarchar(1024)
		 ,clearAddress nvarchar(1024)
		 ,country nvarchar(8)
		 ,city nvarchar(256)
		 ,postalCode nvarchar(32)
		);

		SET @InputDataQuery = 'SELECT address AS rawAddress, address AS address FROM #AddressList';
		INSERT INTO #Responses
		EXECUTE sp_execute_external_script
		@language = N'Python'
	  , @script = N'from geopy.geocoders import Nominatim
import pycountry as pc
#import dbConnect as dbc
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
#Input: key, fullAdress
    #DBConnector:
#addressList = dbc.dbConnect("C:\Users\oleli\Desktop\DA DT materiały\connectionString.txt","SELECT TOP 3 NumerFaktury, AdresKontrahentaJPK_FA FROM da.JPK_FA_VAT;").getData()
#addressDF = pd.DataFrame(addressList, columns=["doc","address"])
    #FileConnector:
#addressDF = pd.read_csv("test.txt",sep=",", index_col=0, header=0)
    #PandasConnector:
data = [["rawAdress","Ul. Wincentego Pola 1 31-532 Kraków Pl"]]
addressDF = pd.DataFrame(data, columns=["doc","address"])
    #SQL Server connector
#adressDF = SQL_in

addressDF["address"] = addressDF["address"].apply(clearAddress)
addressDF["country"], addressDF["city"] = zip(*addressDF["address"].apply(geoDataFromAddress))
addressDF["postalCode"] = addressDF["address"].apply(getPostalCode)
#Output: key, fullAdress, country, city, postalCode
    #OutputToFile:
#addressDF.to_csv("test.txt", sep=",")
    #Output to print
#print(addressDF)
    #Output to SQL Server
SQL_out = adressDF
'
	  , @input_data_1 = @InputDataQuery
	  , @input_data_1_name  = N'SQL_in'
	  , @output_data_1_name =  N'SQL_out';

	--insert checked addresses
	SET @InputDataQuery = N'INSERT INTO '+@schemaName+'.'+@targetTableName+'
							SELECT *, GETDATE() FROM #Responses'
	;
	EXECUTE sp_executeSQL @InputDataQuery;
	SET @AddressesInserted =  @@ROWCOUNT;
		