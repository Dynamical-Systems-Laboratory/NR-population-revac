import csv

#
# The original SafeGraph data are uploaded to Google drive due to the size limit of GitHub
# Link: 
# The data are in groups by year
# with 1 group (5 files) of 2020 and 3 groups (6 files each) of 2021
#

def convertFile(inFileName, outFileName):
    ''' Convert the comma separated file to a tab separated file for future processing '''
    csv.writer(open(outFileName, 'w+'), delimiter='\t').writerows(csv.reader(open(inFileName)))

def filterFile2020(inFileName, outFileName):
    ''' Clean up the 2020 SafeGraph data file, keeping building's name, top_category, latitude, longitude, zip code '''
    with open(inFileName, 'r') as inFile, open(outFileName, 'w') as outFile:
        for line in inFile:
            lineList = line.split('\t')
            newLine = '\t'.join([lineList[2], lineList[5], lineList[8], lineList[9], lineList[13]])
            outFile.write(newLine+'\n')

def filterFile2021(inFileName, outFileName):
    ''' Clean up the 2021 SafeGraph data file, keeping building's name, top_category, latitude, longitude, zip code '''
    with open(inFileName, 'r') as inFile, open(outFileName, 'w') as outFile:
        for line in inFile:
            lineList = line.split('\t')
            newLine = '\t'.join([lineList[4], lineList[7], lineList[10], lineList[11], lineList[15]])
            outFile.write(newLine+'\n')

def preProcessing(year, group=0):
    ''' Pre-process the SafeGraph data, calling the convertFile and filterFile function, output text files '''

    # Note that the 2020 data and 2021 data call different filterFile202x functions accordingly
    # (Since the raw data from 2020 and 2021 has different layout)

    if year == "2020":
        for i in range(1,6):
            inFile = "2020_core_poi-part" + str(i) + ".csv"
            tabFile = "2020_core_poi-part" + str(i) + ".tsv"
            outFile = "2020_poi-part" + str(i) + ".txt"
            convertFile(inFile, tabFile)
            filterFile2020(tabFile, outFile)

    elif year == "2021" and group == 1:
        for i in range(1,7):
            inFile = "2021_core_poi-part" + str(i) + ".csv"
            tabFile = "2021_core_poi-part" + str(i) + ".tsv"
            outFile = "2021_poi-part" + str(i) + ".txt"
            convertFile(inFile, tabFile)
            filterFile2021(tabFile, outFile)

    elif year == "2021" and group == 2:
        for i in range(7, 13):
            inFile = "2021_core_poi-part" + str(i) + ".csv"
            tabFile = "2021_core_poi-part" + str(i) + ".tsv"
            outFile = "2021_poi-part" + str(i) + ".txt"
            convertFile(inFile, tabFile)
            filterFile2021(tabFile, outFile)

    elif year == "2021" and group == 3:
        for i in range(13, 19):
            inFile = "2021_core_poi-part" + str(i) + ".csv"
            tabFile = "2021_core_poi-part" + str(i) + ".tsv"
            outFile = "2021_poi-part" + str(i) + ".txt"
            convertFile(inFile, tabFile)
            filterFile2021(tabFile, outFile)

    else:
        raise Exception("The year/group is not supported.")

def buildLeisureMap():
    ''' Build and return a map that contains all categories that are considered leisure locations '''

    # 1 is a dummy int value that indicates the existence of such key in the map
    # In later part, leisureMap[category] == 1 means such a category is a leisure location
    leisureMap = {}
    leisureMap["Amusement Parks and Arcades"] = 1
    leisureMap["Automobile Dealers"] = 1
    leisureMap["Automotive Equipment Rental and Leasing"] = 1
    leisureMap["Automotive Repair and Maintenance"] = 1
    leisureMap["Bakeries and Tortilla Manufacturing"] = 1
    leisureMap["Beer, Wine, and Liquor Stores"] = 1
    leisureMap["Beverage Manufacturing"] = 1
    leisureMap["Book Stores and News Dealers"] = 1
    leisureMap["Building Material and Supplies Dealers"] = 1
    leisureMap["Child Day Care Services"] = 1
    leisureMap["Clothing Stores"] = 1
    leisureMap["Consumer Goods Rental"] = 1
    leisureMap["Department Stores"] = 1
    leisureMap["Electronics and Appliance Stores"] = 1
    leisureMap["Florists"] = 1
    leisureMap["Furniture Stores"] = 1
    leisureMap["Gasoline Stations"] = 1
    leisureMap["General Medical and Surgical Hospitals"] = 1
    leisureMap["General Merchandise Stores"] = 1
    leisureMap["General Merchandise Stores, including Warehouse Clubs and Supercenters"] = 1
    leisureMap["Grocery Stores"] = 1
    leisureMap["Health and Personal Care Stores"] = 1
    leisureMap["Home Furnishings Stores"] = 1
    leisureMap["Home Health Care Services"] = 1
    leisureMap["Interurban and Rural Bus Transportation"] = 1
    leisureMap["Jewelry Luggage and Leather Goods Stores"] = 1
    leisureMap["Lessors of Real Estate"] = 1
    leisureMap["Liquor Stores"] = 1
    leisureMap["Miscellaneous Durable Goods Merchant Wholesalers"] = 1
    leisureMap["Motion Picture and Video Industries"] = 1
    leisureMap["Museums, Historical Sites, and Similar Institutions"] = 1
    leisureMap["Nursing Care Facilities (Skilled Nursing Facilities)"] = 1
    leisureMap["Office Supplies, Stationery, and Gift Stores"] = 1
    leisureMap["Other Ambulatory Health Care Services"] = 1
    leisureMap["Other Amusement and Recreation Industries"] = 1
    leisureMap["Other Miscellaneous Store Retailers"] = 1
    leisureMap["Other Motor Vehicle Dealers"] = 1
    leisureMap["Other Personal Services"] = 1
    leisureMap["Personal Care Services"] = 1
    leisureMap["Rail Transportation"] = 1
    leisureMap["Religious Organizations"] = 1
    leisureMap["Restaurants and Other Eating Places"] = 1
    leisureMap["Shoe Stores"] = 1
    leisureMap["Specialty Food Stores"] = 1
    leisureMap["Spectator Sports"] = 1
    leisureMap["Sporting Goods, Hobby, and Musical Instrument Stores"] = 1
    leisureMap["Travel Arrangement and Reservation Services"] = 1
    leisureMap["Traveler Accommodation"] = 1
    leisureMap["Used Merchandise Stores"] = 1
    return leisureMap

def buildWorkMap():
    ''' Build and return a map that contains all categories that are NOT considered workplaces '''

    # 1 is a dummy int value that indicates the existence of such key in the map
    # In later part, leisureMap[category] == 1 means such a category is NOT a leisure location
    workMap = {}
    workMap["Child Day Care Services"] = 1
    workMap["Colleges, Universities, and Professional Schools"] = 1
    workMap["Elementary and Secondary Schools"] = 1
    workMap["Home Health Care Services"] = 1
    workMap["Medical and Diagnostic Laboratories"] = 1
    workMap["Nursing Care Facilities (Skilled Nursing Facilities)"] = 1
    workMap["Other Ambulatory Health Care Services"] = 1
    workMap["Other Schools and Instruction"] = 1
    workMap["Outpatient Care Centers"] = 1
    workMap["Personal Care Services"] = 1
    workMap["Psychiatric and Substance Abuse Hospitals"] = 1
    workMap["Continuing_Care_Retirement_Communities_and_Assisted_Living_Facilities_for_the_Elderly"] = 1
    workMap["General_Medical_and_Surgical_Hospitals"] = 1
    workMap["Junior_Colleges"] = 1
    return workMap

def getInTownZip(cityName):
    ''' Build and return a list of all zip codes in-town for the city '''

    if cityName == "Utica":
        return ["13501", "13502", "13503", "13504", "13505", "13599"]
    elif cityName == "Colonie":
        return ["12205", "12110", "12309", "12047", "12303", "12189", "12203", "12304", "12211"]
    elif cityName == "NewRochelle":
        return ["10801", "10805", "10804", "10583", "10803", "10538"]
    else:
        print("getInTownZip: city name " + cityName + " not supported.")
        return False

def getOutOfTownZip(cityName):
    ''' Build and return a list of all zip codes out-of-town for the city '''

    if cityName == "Utica":
        return ["13440", "13413", "13340", "13323", "13357", "13403", "13350", "13456",\
                "13417", "13421", "13365"]
    elif cityName == "Colonie":
        return ["12180", "12065", "12306", "12302", "12020", "12144", "12866", "12208", "12206", \
                "12054", "12182", "12308", "12188", "12118", "12019", "12204"]
    elif cityName == "NewRochelle":
        return ["10550", "10466", "10701", "10469", "10567", "10552", "10573", "10543",\
                "10704", "10475", "10710"]
    else:
        print("getOutOfTownZip: city name " + cityName + " not supported.")
        return False

def matchCategory():
    ''' Build and return a map from SafeGraph category to business category '''

    catMap = {}
    with open("TopCat_Codes.tsv", 'r') as inFile:
        next(inFile)
        for line in inFile:
            infoList = line.split('\t')
            catMap[infoList[0]] = infoList[1]

    return catMap

def matchUncat():
    ''' Build and return a map from key word in uncategorized buildings' names to business category '''

    catMap = {}
    with open("uncategorized_key_words.tsv", 'r') as inFile:
        next(inFile)
        for line in inFile:
            infoList = line.split('\t')
            catMap[infoList[0]] = infoList[2]

    return catMap

def matchTopCatOcc():
    ''' Build and return a map from SafeGraph category to occupation '''

    occMap = {}
    with open("match_topcat_occupation.tsv", 'r') as inFile:
        next(inFile)
        for line in inFile:
            infoList = line.split('\t')
            occMap[infoList[0]] = infoList[2]

    return occMap

def matchCatCodeOcc():
    ''' Build and return a map from key word in uncategoirzed buildings' names to occupation '''

    occMap = {}
    with open("match_catcode_occupation.tsv", 'r') as inFile:
        next(inFile)
        for line in inFile:
            infoList = line.split('\t')
            occMap[infoList[0]] = infoList[2]

    return occMap

def printIgnored(countIgnored, countTotal, city, category, inOrOut):
    if countTotal != 0:
        percent = countIgnored / countTotal * 100
    else:
        percent = 0
    print(countIgnored, ",", percent, "% uncategorized buildings were ignored in", \
          city, category, inOrOut)

def cleanLeisure(inFileNameList, outFileName, cityName, inOrOut):
    ''' Output all leisure locations in/out-of-town in given city, return number of ignored & total buildings '''

    leisureMap = buildLeisureMap()
    unCatMap = matchUncat()
    countIgnored = 0
    countTotal = 0

    if inOrOut == "in":
        zipList = getInTownZip(cityName)
    elif inOrOut == "out":
        zipList = getOutOfTownZip(cityName)
    else:
        return False

    with open(outFileName, 'w') as outFile:
        print("location_name\ttop_category\tlatitude\tlongitude", file=outFile)
        for eachFileName in inFileNameList:
            with open(eachFileName, 'r') as inFile:
                next(inFile)
                for line in inFile:
                    infoList = line.split('\t')
                    zipcode = infoList[4].strip()
                    if zipcode in zipList:
                        if infoList[1] == '': # uncategorized
                            posName = infoList[0].split()
                            for word in posName:
                                if infoList[1] != '':
                                    break
                                try:
                                    infoList[1] = unCatMap[word]
                                except KeyError:
                                    continue
                            if infoList[1] == '':
                                countIgnored += 1
                        try:
                            if (leisureMap[infoList[1]] == 1):
                                newLine = '\t'.join(infoList[:4])
                                countTotal += 1
                                print(newLine, file=outFile)
                        except KeyError: # top_category not in leisureMap
                            continue

    printIgnored(countIgnored, countTotal, cityName, "leisure", inOrOut)

def cleanWork(inFileNameList, outFileName, cityName, inOrOut, occupation = False):
    ''' Output all workplaces in/out-of-town in given city, return number of ignored & total buildings '''

    workMap = buildWorkMap()
    catMap = matchCategory()
    unCatMap = matchUncat()
    occMap_Top = matchTopCatOcc()
    occMap_Code = matchCatCodeOcc()
    countIgnored = 0
    countTotal = 0

    if inOrOut == "in":
        zipList = getInTownZip(cityName)
    elif inOrOut == "out":
        zipList = getOutOfTownZip(cityName)
    else:
        return False

    with open(outFileName, 'w') as outFile:
        if occupation:
            print("location_name\toccupation\tlatitude\tlongitude", file=outFile)
        else:
            print("location_name\tcategory\tlatitude\tlongitude", file=outFile)
        for eachFileName in inFileNameList:
            with open(eachFileName, 'r') as inFile:
                next(inFile)
                for line in inFile:
                    infoList = line.split('\t')
                    zipcode = infoList[4].strip()
                    if zipcode in zipList:
                        if infoList[1] == '': # uncategorized
                            posName = infoList[0].split()
                            infoList[1] = ''
                            for word in posName:
                                if infoList[1] != '':
                                    break
                                try:
                                    infoList[1] = unCatMap[word]
                                except KeyError:
                                    continue
                            if infoList[1] == '':
                                countIgnored += 1
                        if occupation: # get occupation
                            try:
                                infoList[1] = occMap_Code[infoList[1]]
                            except KeyError:
                                try:
                                    infoList[1] = occMap_Top[infoList[1]]
                                except KeyError:
                                    continue
                            newLine = '\t'.join(infoList[:4])
                            countTotal += 1
                            print(newLine, file=outFile)
                        else: # get workplaces
                            try:
                                if (workMap[infoList[1]] == 1):
                                    pass
                            except KeyError:  # building is a workplace
                                topCat = infoList[1]
                                try:
                                    infoList[1] = catMap[topCat]
                                except KeyError:
                                    continue
                                newLine = '\t'.join(infoList[:4])
                                countTotal += 1
                                print(newLine, file=outFile)
    if occupation:
        printIgnored(countIgnored, countTotal, cityName, "occupation", inOrOut)
    else:
        printIgnored(countIgnored, countTotal, cityName, "work", inOrOut)

def dataProcessing(city, category, year, group=0):
    ''' Process SafeGraph data for given city, category, year, and group(optional) '''

    if category == "leisure":
        if year == "2020":
            cleanLeisure(["2020_poi-part1.txt", "2020_poi-part2.txt", "2020_poi-part3.txt", \
                    "2020_poi-part4.txt", "2020_poi-part5.txt"], "2020_core_poi_"+city+"In_LeisureTrimmed.csv", city, "in")
            cleanLeisure(["2020_poi-part1.txt", "2020_poi-part2.txt", "2020_poi-part3.txt", \
                    "2020_poi-part4.txt", "2020_poi-part5.txt"], "2020_core_poi_"+city+"Out_LeisureTrimmed.csv", city, "out")

        elif year == "2021":
            if group == 1:
                cleanLeisure(["2021_poi-part1.txt", "2021_poi-part2.txt", "2021_poi-part3.txt", \
                             "2021_poi-part4.txt", "2021_poi-part5.txt", "2021_poi-part5.txt"], \
                             "2021_1_core_poi_"+city+"In_LeisureTrimmed.csv", city, "in")
                cleanLeisure(["2021_poi-part1.txt", "2021_poi-part2.txt", "2021_poi-part3.txt", \
                             "2021_poi-part4.txt", "2021_poi-part5.txt", "2021_poi-part6.txt"], \
                             "2021_1_core_poi_"+city+"Out_LeisureTrimmed.csv", city, "out")

            elif group == 2:
                cleanLeisure(["2021_poi-part7.txt", "2021_poi-part8.txt", "2021_poi-part9.txt", \
                             "2021_poi-part10.txt", "2021_poi-part11.txt", "2021_poi-part12.txt"], \
                             "2021_2_core_poi_"+city+"In_LeisureTrimmed.csv", city, "in")
                cleanLeisure(["2021_poi-part7.txt", "2021_poi-part8.txt", "2021_poi-part9.txt", \
                             "2021_poi-part10.txt", "2021_poi-part11.txt", "2021_poi-part12.txt"], \
                             "2021_2_core_poi_"+city+"Out_LeisureTrimmed.csv", city, "out")

            elif group == 3:
                cleanLeisure(["2021_poi-part13.txt", "2021_poi-part14.txt", "2021_poi-part15.txt",\
                             "2021_poi-part16.txt", "2021_poi-part17.txt", "2021_poi-part18.txt"], \
                             "2021_3_core_poi_"+city+"In_LeisureTrimmed.csv", city, "in")
                cleanLeisure(["2021_poi-part13.txt", "2021_poi-part14.txt", "2021_poi-part15.txt", \
                             "2021_poi-part16.txt", "2021_poi-part17.txt", "2021_poi-part18.txt"], \
                             "2021_3_core_poi_"+city+"Out_LeisureTrimmed.csv", city, "out")

            else:
                raise Exception("The group is not supported.")
        else:
            raise Exception("The year is not supported.")

    elif category == "work":
        if year == "2020":
            cleanWork(["2020_poi-part1.txt", "2020_poi-part2.txt", "2020_poi-part3.txt", \
                          "2020_poi-part4.txt", "2020_poi-part5.txt"], "2020_core_poi_"+city+"In_WorkTrimmed.csv", city, "in")
            cleanWork(["2020_poi-part1.txt", "2020_poi-part2.txt", "2020_poi-part3.txt", \
                          "2020_poi-part4.txt", "2020_poi-part5.txt"], "2020_core_poi_"+city+"Out_WorkTrimmed.csv", city, "out")

        elif year == "2021":
            if group == 1:
                cleanWork(["2021_poi-part1.txt", "2021_poi-part2.txt", "2021_poi-part3.txt", \
                             "2021_poi-part4.txt", "2021_poi-part5.txt", "2021_poi-part6.txt"], \
                             "2021_1_core_poi_"+city+"In_WorkTrimmed.csv", city, "in")
                cleanWork(["2021_poi-part1.txt", "2021_poi-part2.txt", "2021_poi-part3.txt", \
                             "2021_poi-part4.txt", "2021_poi-part5.txt", "2021_poi-part6.txt"], \
                             "2021_1_core_poi_"+city+"Out_WorkTrimmed.csv", city, "out")

            elif group == 2:
                cleanWork(["2021_poi-part7.txt", "2021_poi-part8.txt", "2021_poi-part9.txt", \
                             "2021_poi-part10.txt", "2021_poi-part11.txt", "2021_poi-part12.txt"], \
                             "2021_2_core_poi_"+city+"In_WorkTrimmed.csv", city, "in")
                cleanWork(["2021_poi-part7.txt", "2021_poi-part8.txt", "2021_poi-part9.txt", \
                             "2021_poi-part10.txt", "2021_poi-part11.txt", "2021_poi-part12.txt"], \
                             "2021_2_core_poi_"+city+"Out_WorkTrimmed.csv", city, "out")

            elif group == 3:
                cleanWork(["2021_poi-part13.txt", "2021_poi-part14.txt", "2021_poi-part15.txt", \
                             "2021_poi-part16.txt", "2021_poi-part17.txt", "2021_poi-part18.txt"], \
                             "2021_3_core_poi_"+city+"In_WorkTrimmed.csv", city, "in")
                cleanWork(["2021_poi-part13.txt", "2021_poi-part14.txt", "2021_poi-part15.txt", \
                             "2021_poi-part16.txt", "2021_poi-part17.txt", "2021_poi-part18.txt"], \
                             "2021_3_core_poi_"+city+"Out_WorkTrimmed.csv", city, "out")

            else:
                raise Exception("The group is not supported.")
        else:
            raise Exception("The year is not supported.")

    elif category == "occupation":
        if year == "2020":
            cleanWork(["2020_poi-part1.txt", "2020_poi-part2.txt", "2020_poi-part3.txt", \
                  "2020_poi-part4.txt", "2020_poi-part5.txt"], "2020_core_poi_"+city+"In_OccupationTrimmed.csv", city, "in", True)
            cleanWork(["2020_poi-part1.txt", "2020_poi-part2.txt", "2020_poi-part3.txt", \
                  "2020_poi-part4.txt", "2020_poi-part5.txt"], "2020_core_poi_"+city+"Out_OccupationTrimmed.csv", city, "out", True)

        elif year == "2021":
            if group == 1:
                cleanWork(["2021_poi-part1.txt", "2021_poi-part2.txt", "2021_poi-part3.txt", \
                             "2021_poi-part4.txt", "2021_poi-part5.txt", "2021_poi-part6.txt"], \
                             "2021_1_core_poi_"+city+"In_OccupationTrimmed.csv", city, "in", True)
                cleanWork(["2021_poi-part1.txt", "2021_poi-part2.txt", "2021_poi-part3.txt", \
                             "2021_poi-part4.txt", "2021_poi-part5.txt", "2021_poi-part6.txt"], \
                             "2021_1_core_poi_"+city+"Out_OccupationTrimmed.csv", city, "out", True)

            elif group == 2:
                cleanWork(["2021_poi-part7.txt", "2021_poi-part8.txt", "2021_poi-part9.txt", \
                             "2021_poi-part10.txt", "2021_poi-part11.txt", "2021_poi-part12.txt"], \
                             "2021_2_core_poi_"+city+"In_OccupationTrimmed.csv", city, "in", True)
                cleanWork(["2021_poi-part7.txt", "2021_poi-part8.txt", "2021_poi-part9.txt", \
                             "2021_poi-part10.txt", "2021_poi-part11.txt", "2021_poi-part12.txt"], \
                             "2021_2_core_poi_"+city+"Out_OccupationTrimmed.csv", city, "out", True)

            elif group == 3:
                cleanWork(["2021_poi-part13.txt", "2021_poi-part14.txt", "2021_poi-part15.txt", "2021_poi-part16.txt", \
                     "2021_poi-part17.txt", "2021_poi-part18.txt"], \
                    "2021_3_core_poi_"+city+"In_OccupationTrimmed.csv", city, "in", True)
                cleanWork(["2021_poi-part13.txt", "2021_poi-part14.txt", "2021_poi-part15.txt", "2021_poi-part16.txt", \
                     "2021_poi-part17.txt", "2021_poi-part18.txt"], \
                    "2021_3_core_poi_"+city+"Out_OccupationTrimmed.csv", city, "out", True)

            else:
                raise Exception("The group is not supported.")
        else:
            raise Exception("The year is not supported.")

    else:
        raise Exception("The category is not supported.")

def testMain():
    # Pre-processing for sample test file
    convertFile("test_file_2020_raw_safegraph.csv", "test_file_2020_raw_safegraph.tsv")
    filterFile2020("test_file_2020_raw_safegraph.tsv", "test_file_2020_clean_safegraph.txt")
    convertFile("test_file_2021_raw_safegraph.csv", "test_file_2021_raw_safegraph.tsv")
    filterFile2021("test_file_2021_raw_safegraph.tsv", "test_file_2021_clean_safegraph.txt")

    # Data processing for sample test file
    cleanLeisure(["test_file_2020_clean_safegraph.txt"], "2020_core_poi_" + "Utica" + "In_LeisureTrimmed.csv", \
                 "Utica", "in")
    cleanWork(["test_file_2020_clean_safegraph.txt"], "2020_core_poi_" + "Utica" + "In_WorkTrimmed.csv", \
              "Utica", "in")
    cleanWork(["test_file_2020_clean_safegraph.txt"], "2020_core_poi_" + "Utica" + "Out_OccupationTrimmed.csv", \
              "Utica", "out", True) # Occupation
    cleanLeisure(["test_file_2021_clean_safegraph.txt"], "2021_core_poi_" + "Colonie" + "In_LeisureTrimmed.csv", \
                 "Colonie", "in")
    cleanWork(["test_file_2021_clean_safegraph.txt"], "2021_core_poi_" + "Colonie" + "In_WorkTrimmed.csv", \
              "Colonie", "in")
    cleanWork(["test_file_2021_clean_safegraph.txt"], "2021_core_poi_" + "Colonie" + "Out_OccupationTrimmed.csv", \
              "Colonie", "out", True) # Occupation
        
if __name__ == '__main__':
    # For running test files
    #testMain()

    # Pre-process SafeGraph data to get a text file with buildings' name, top_category, latitude, longitude, zip code
    # preProcessing(year, group), where param "group" is optional

    preProcessing("2020")
    preProcessing("2021", 1)
    preProcessing("2021", 2)
    preProcessing("2021", 3)

    # Process SafeGraph data for specific city, category, and time frame
    # city: Utica, Colonie, NewRochelle (note: no spaces)
    # category: leisure, work, occupation
    # year: 2020, 2021
    # group: (only for year 2021) 1, 2, 3
    # dataProcessing(city, category, year, group), where param "group" is optional

    dataProcessing("Utica", "leisure", "2020")
    dataProcessing("Utica", "leisure", "2021", 1)
    dataProcessing("Utica", "leisure", "2021", 2)
    dataProcessing("Utica", "leisure", "2021", 3)
    dataProcessing("Colonie", "leisure", "2020")
    dataProcessing("Colonie", "leisure", "2021", 1)
    dataProcessing("Colonie", "leisure", "2021", 2)
    dataProcessing("Colonie", "leisure", "2021", 3)
    dataProcessing("NewRochelle", "leisure", "2020")
    dataProcessing("NewRochelle", "leisure", "2021", 1)
    dataProcessing("NewRochelle", "leisure", "2021", 2)
    dataProcessing("NewRochelle", "leisure", "2021", 3)

    dataProcessing("Utica", "work", "2020")
    dataProcessing("Utica", "work", "2021", 1)
    dataProcessing("Utica", "work", "2021", 2)
    dataProcessing("Utica", "work", "2021", 3)
    dataProcessing("Colonie", "work", "2020")
    dataProcessing("Colonie", "work", "2021", 1)
    dataProcessing("Colonie", "work", "2021", 2)
    dataProcessing("Colonie", "work", "2021", 3)
    dataProcessing("NewRochelle", "work", "2020")
    dataProcessing("NewRochelle", "work", "2021", 1)
    dataProcessing("NewRochelle", "work", "2021", 2)
    dataProcessing("NewRochelle", "work", "2021", 3)

    dataProcessing("Utica", "occupation", "2020")
    dataProcessing("Utica", "occupation", "2021", 1)
    dataProcessing("Utica", "occupation", "2021", 2)
    dataProcessing("Utica", "occupation", "2021", 3)
    dataProcessing("Colonie", "occupation", "2020")
    dataProcessing("Colonie", "occupation", "2021", 1)
    dataProcessing("Colonie", "occupation", "2021", 2)
    dataProcessing("Colonie", "occupation", "2021", 3)
    dataProcessing("NewRochelle", "occupation", "2020")
    dataProcessing("NewRochelle", "occupation", "2021", 1)
    dataProcessing("NewRochelle", "occupation", "2021", 2)
    dataProcessing("NewRochelle", "occupation", "2021", 3)

