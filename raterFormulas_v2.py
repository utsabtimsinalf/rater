class policy:    
    
    def totalPremium(self):
        
        totalPremium = 0
        for vehicle in self.vehicles:
            totalPremium += vehicle.totalPremium
        
    return round(totalPremium,0)

    #input fields
    #PolicyPeriod
    #AccountCredit
    #YearsInsuredWithFAIRPlan
    #ContinuouslyInsuredFor12Months
    
    #derived Data
    def calcLevelOneData(self):
        
        #Tier Factors (these are all small lookup tables in Tier tab)
        self.derivedData['AccountTier'] = 'A' if self.inputs['AccountCredit'] == 'Yes' else 'B'        
        
        if self.inputs['YearsInsuredWithFAIRPlan'] == '0': #note the string value
            self.derivedData['YearsInsuredTier'] = 'A'
        elif self.inputs['YearsInsuredWithFAIRPlan'] == '1':
            self.derivedData['YearsInsuredTier'] = 'B'
        elif self.inputs['YearsInsuredWithFAIRPlan'] == '2':
            self.derivedData['YearsInsuredTier'] = 'C'
        elif self.inputs['YearsInsuredWithFAIRPlan'] == '3':
            self.derivedData['YearsInsuredTier'] = 'D'
        elif self.inputs['YearsInsuredWithFAIRPlan'] in ('4', '5','6','7'):
            self.derivedData['YearsInsuredTier'] = 'E'
        elif self.inputs['YearsInsuredWithFAIRPlan'] == '8+':
            self.derivedData['YearsInsuredTier'] = 'F'
        else:
            raise InvalidInput('Policy:YearsInsuredWithFAIRPlan')
        
        self.derivedData['ContinuouslyTier'] = 'A' if self.inputs['ContinuouslyInsuredFor12Months'] == 'Yes' else 'B'
        
        #multi-car does not count antique cars
        carCount = 0
        for vehicle in self.vehicles:
            carCount += 1
            if vehicle.inputs['Antique'] == 'Yes':
                carCount -= 1
                
        self.derivedData['MultiCarDiscount'] = 'Yes' if carCount > 1 else 'No'

        self.derivedData['MultiCarTier'] = 'A' if self.derivedData['MultiCarDiscount'] == 'Yes' else 'B'
        
        #least favorable merit rating logic is interesting. from best to worst: 99 -> 98 -> 0 -> 1 ->... -> 45
        leastFavorableRating = 99
        for driver in self.drivers:
            if leastFavorableRating >= 98:             
                if driver.inputs['MeritRatingPoints'] < leastFavorableRating:
                    leastFavorableRating = self.driver.inputs['MeritRatingPoints']
            else:
                if driver.inputs['MeritRatingPoints'] > leastFavorableRating and driver.inputs['MeritRatingPoints'] > 98:
                    leastFavorableRating = driver.inputs['MeritRatingPoints']
        self.derivedData['LeastFavorableRating'] = leastFavorableRating
        
        if self.derivedData['LeastFavorableRating'] == 99:
            self.derivedData['LeastFavorableTier'] = 'A'
        elif self.derivedData['LeastFavorableRating'] == 98:
            self.derivedData['LeastFavorableTier'] = 'B'
        elif 0 <= self.derivedData['LeastFavorableRating'] and self.derivedData['LeastFavorableRating'] <= 4:
            self.derivedData['LeastFavorableTier'] = 'C'
        else: # >=5 but < 98            
            self.derivedData['LeastFavorableTier'] = 'D'
            
        part9ForAllVehicles = 'Yes'
        for vehicle in vehicles:
            if vehicle.coverages['Part9'] == 'No':
                part9ForAllVehicles = 'No'
        
        self.derivedData['Part9ForAllVehicles'] = part9ForAllVehicles
        self.derivedData['Part9Tier'] = 'A' if part9ForAllVehicles == 'Yes' else 'No'
        
        #Tier Results from tier table lookup:
        #lookup_TierTable[AccountTier][YearsInsuredTier][ContinuouslyTier][MultiCarTier][LeastFavorableTier][Part9Tier] ==> {'Tier': 1, 'RatingPlan': 'A', 'TierFactor': 0.9455, 'TierScoreBand': 8}

        result = lookup_TierTable(AccountTier=self.derivedData['AccountTier']
                                    , YearsInsuredTier=self.derivedData['YearsInsuredTier']
                                    , ContinuouslyTier=self.derivedData['ContinuouslyTier']
                                    , MultiCarTier=self.derivedData['MultiCarTier']
                                    , LeastFavorableTier=self.derivedData['LeastFavorableTier']
                                    , Part9Tier=self.derivedData['Part9Tier'])

        self.derivedData['Tier'] = result['Tier']
        self.derivedData['RatingPlan'] = result['RatingPlan']
        self.derivedData['TierFactor'] = result['TierFactor']
        self.derivedData['TierScoreBand'] = result['TierScoreBand']
        
        #e-customer/multicar
        #currently using carCount from multicar above
        #if this is wrong, uncomment below
        #carCount = len(self.vehicles)
        if self.inputs['OptingElectronicPolicy'] == 'No':
            self.derivedData['MultiCarType'] == 'No'
        else:
            if carCount == 1:
                if self.inputs['ContinuouslyInsuredFor12Months'] == 'Yes':
                    self.derivedData['MultiCarType'] == 'Mono-line'
                else:
                    self.derivedData['MultiCarType'] == 'No'
            else:
                if carCount > 1 and self.inputs['FirstPolicyIssuance'] == 'Yes':
                    if self.inputs['SelectedBeforeFirstIssuance'] == 'Yes':
                        self.derivedData['MultiCarType'] == 'Mono-line Multi-car - Qualified'
                    elif self.inputs['ContinuouslyInsuredFor12Months'] == 'Yes':
                        self.derivedData['MultiCarType'] == 'Mono-line Multi-car - Unqualified'
                    else:
                        self.derivedData['MultiCarType'] == 'No'
                else:
                    if self.inputs['ContinuouslyInsuredFor12Months'] == 'Yes':
                        self.derivedData['MultiCarType'] == 'Mono-line Multi-car - Renewal'
                    else:
                        self.derivedData['MultiCarType'] == 'No'
            

class applicant:

class driver:
    #when instantiated, pull driverId from the input set
   
    #input fields:
    #DriverAge
    
    def calcLevelOneData(self):
        #annual mileage YL
        if 0 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 47:
            self.derivedData['AnnualMileageYL'] = '<48'
        elif 48 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 98:
            self.derivedData['AnnualMileageYL'] = '>47'
        else:
            self.derivedData['AnnualMileageYL'] = '<48'
        
        #extra risk factors
        # The driver level extra risk factors are level 1 (depending on inputs and lookups), but the actual logic is still being worked on
        #        self.derivedData['CollisionRiskFactor'] = self.inputs['VehicularHomicide'] == 'Yes' * lookup_

    def calcLevelTwoData(self):
        #operator class
        #operator Class feeders depend on policy.derivedData['RatingPlan'], so this needs lvl 2
        #operator class is on a per vehicle basis
        self.derivedData['DriverAgeClass'] = '65+' if self.inputs['DriverAge'] >= 65 else '<65'
        
        if self.policy.derivedData['RatingPlan'] == 'A': #logic build from Licenced_Class
            if 0 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 5:
                self.derivedData['YearsLicensedClass'] = str(self.inputs['YearsLicensed']) #note string here
            elif 6 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 9:
                self.derivedData['YearsLicensedClass'] = '6-9'
            elif 10 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 14:
                self.derivedData['YearsLicensedClass'] = '10-14'
            elif 15 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 19:
                self.derivedData['YearsLicensedClass'] = '15-19'
            elif 20 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 28:
                self.derivedData['YearsLicensedClass'] = '20-28'
            elif 29 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 38:
                self.derivedData['YearsLicensedClass'] = '29-38'
            elif 39 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 48:
                self.derivedData['YearsLicensedClass'] = '39-48'
            elif 49 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 58:
                self.derivedData['YearsLicensedClass'] = '49-58'
            else: # >= 59
                self.derivedData['YearsLicensedClass'] = '59+'
        elif self.policy.derivedData['RatingPlan'] == 'B': #built from LicencedB_Class
            if 0 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 2:
                self.derivedData['YearsLicensedClass'] = '<3'
            elif 3 <= self.inputs['YearsLicensed'] and self.inputs['YearsLicensed'] <= 5:
                self.derivedData['YearsLicensedClass'] = '3-5'
            else: # >= 6
                self.derivedData['YearsLicensedClass'] = '6+'
        else:
            raise InvalidRatingPlan()
        
        for vehicle in policy.vehicles: 
            if vehicle.inputs['AutoUsedInBusiness'] == 'Yes' and self.inputs['YearsLicensed'] > 5:
                self.derivedData['OperatorClass'][vehicle.vehicleId] = 30
            elif self.policy.derivedData['RatingPlan'] == 'A':                
                result = lookup_ClassATable(operatorType=self.inputs['OperatorType'][vehicle.vehicleId]
                                                , licencedClass=self.derivedData['YearsLicensedClass']
                                                , driverAge=self.derivedData['DriverAgeClass']
                                                , vehicleBusiness=vehicle.inputs['AutoUsedInBusiness'] 
                                                , driverTraining=self.inputs['DriverTraining'])
                self.derivedData['OperatorClass'][vehicle.vehicleId] = result['OperatorClass']
                if ( 50 <= self.derivedData['OperatorClass'][vehicle.vehicleId] and self.derivedData['OperatorClass'][vehicle.vehicleId] <= 57 )
                    or ( 60 <= self.derivedData['OperatorClass'][vehicle.vehicleId] and self.derivedData['OperatorClass'][vehicle.vehicleId] <= 67 )
                    or ( self.derivedData['OperatorClass'][vehicle.vehicleId] == 30 ):
                    
                    self.derivedData['OperatorClassType'][vehicle.vehicleId] = 'Experienced'
                else:
                    self.derivedData['OperatorClassType'][vehicle.vehicleId] = 'Inexperienced'
            elif self.policy.derivedData['RatingPlan'] == 'B':                
                result = lookup_ClassBTable(operatorType=self.inputs['OperatorType'][vehicle.vehicleId]
                                                , licencedClass=self.derivedData['YearsLicensedClass']
                                                , driverAge=self.derivedData['DriverAgeClass']
                                                , vehicleBusiness=vehicle.inputs['AutoUsedInBusiness'] 
                                                , driverTraining=self.inputs['DriverTraining'])
                self.derivedData['OperatorClass'][vehicle.vehicleId] = result['OperatorClass']

                if self.derivedData['OperatorClass'][vehicle.vehicleId] in (10, 15, 30):
                   self.derivedData['OperatorClassType'][vehicle.vehicleId] = 'Experienced'
                else:
                    self.derivedData['OperatorClassType'][vehicle.vehicleId] = 'Inexperienced'
            else:
                raise InvalidRatingPlan()
                
        #student discounts
        #good student
        if self.inputs['DriverGoodStudent'] == 'Yes' and self.policy.inputs['RatingPlan'] == 'A' and self.inputs['YearsLicensed'] <= 3 and ( self.inputs['MeritRatingPoints'] <= 4 or self.inputs['MeritRatingPoints'] >= 98 ):
            self.derivedData['DriverGoodStudentDiscount'] = 'Yes'
        else:
            self.derivedData['DriverGoodStudentDiscount'] = 'No'
        
        #away student
        if self.policy['DriverAwayStudent'] =='Yes' and self.policy.inputs['RatingPlan'] == 'A' and self.inputs['YearsLicensed'] <= 3 and ( self.inputs['MeritRatingPoints'] <= 4 or self.inputs['MeritRatingPoints'] >= 98 ):
            self.derivedData['DriverAwayStudentDiscount'] = 'Yes'
        else:
            self.derivedData['DriverAwayStudentDiscount'] = 'No'
            
class vehicle:
    #when instantiating pull vehicleId from input set
    
    def totalPremium(self):
        totalPremium = 0
        for part in vehicle.premiumParts
            totalPremium += part.totalPremium
        
        totalPremium += self.derivedData['excessElectronicEquipmentPremium'] +  self.derivedData['autoLoanLeaseGapCoveragePremium'] 
        return round(totalPremium,0)
    
    #coverage selection for vehicles should be a dict passed in from the FE
    
    def calcLevelOneData(self, policy):
        #extra vehicle lvl premiums
        self.derivedData['excessElectronicEquipmentPremium'] = (self.inputs['excessEquipmentCoverage'] - 1000) / 100 * 4 #all numbers here look like policy defaults?  it looks like this is "coverage costs $4 per $100 over base $1000 coverages"
                
        self.derivedData['autoLoanLeaseGapCoveragePremium'] = 25 if self.inputs['AutoLoanLeaseGapCoverage'] == 'Yes' else 0  #the $25 is probably a policy default.  
        
        #model year and mileage
        if self.inputs['useOfOtherAutos'] =='Yes' or self.policy['PolicyEffectiveYear'] - self.inputs['ModelYear'] <= 0:   #it is possible to buy a 2023 model year car in calendar year 2022, so cut off at 0
            self.derivedData['VehicleAge'] = '0'   #note the string
        elif self.policy['PolicyEffectiveYear'] - self.inputs['ModelYear'] >= 14:
            self.derivedData['VehicleAge'] = '14+'  #the reason for the string
        else:
            self.derivedData['VehicleAge'] = str(self.policy['PolicyEffectiveYear'] - self.inputs['ModelYear'])
            
        if self.inputs['useOfOtherAutos'] =='Yes' or self.inputs['ModelYear'] >= 2020: 
            self.derivedData['ModelYearClass'] = '2020'   #note the string
        elif self.inputs['ModelYear'] < 1990:
            self.derivedData['ModelYearClass'] = '1989 & Prior'  #the reason for the string
        elif 1990 <= self.inputs['ModelYear'] and self.inputs['ModelYear'] <= 2008:
            self.derivedData['ModelYearClass'] = '1990-2008'  #the reason for the string
        else:
            self.derivedData['ModelYearClass'] = str(self.inputs['ModelYear'])
            
        if self.inputs['AnnualMileage'] <= 5000:
            self.derivedData['AnnualMileageClass'] = '0-5000'
        elif 5001 <= self.inputs['AnnualMileage'] and self.inputs['AnnualMileage'] <= 7500:
            self.derivedData['AnnualMileageClass'] = '5001-7500'
        else:
            self.derivedData['AnnualMileageClass'] = 'None'
            
            
    def calcLevelTwoData(self, policy):
        #low Frequency
        if self.policy.derivedData['RatingPlan'] == 'B':
            if ( self.assignedDriver.inputs['MeritRatingPoints'] < 4 or self.assignedDriver.inputs['MeritRatingPoints'] >= 98 ) and ( self.assignedDriver.inputs['NoClaimsInPast3Years'] == 'Yes' ):
                self.derivedData['LowFrequency'] = 'Yes'                
            else:
                self.derivedData['LowFrequency'] = 'No'                
        else:
            self.derivedData['LowFrequency'] = 'No'

        #basic Package qualifications
        isMeritRatingBasic = True
        for driver in self.drivers:
            if not ( ( 0 <= driver.inputs['MeritRatingPoints'] and driver.inputs['MeritRatingPoints'] <= 4 ) or ( driver.inputs['MeritRatingPoints'] >= 98 ) ):
                isMeritRatingBasic = False
        
        isBasicPlan = self.coverages['Part1'] == '$20/40' and self.coverages['Part2'] == 8000 and self.coverages['Part3'] == '$20/40' 
                        and self.coverages['Part4'] == 5000 and self.coverages['Part5'] == '$20/40' and self.coverages['Part6'] == 'None' 
                        and self.coverages['Part7'] == 'No' and self.coverages['Part8'] == 'No' and self.coverages['Part9'] == 'No' 
                        and self.coverages['Part10'] == 'None' and self.coverages['Part11'] == 'None' and ( self.coverages['Part12'] == 'None' or self.coverages['Part12'] == '$20/40' )
                
        if self.policy['RatingPlan'] == 'A' and self.policy.inputs.['ContinuouslyInsuredFor12Months'] == 'Yes' and isMeritRatingBasic and isBasicPlan and self.inputs['PIPDeductible'] == 0:
            self.derivedData['BasicPlanQualified'] = 'Yes'
        else:
            self.derivedData['BasicPlanQualified'] = 'No'            
        
         
    def calcLevelThreeData(self, policy):
        #basic plan applies - depends on basic plan qualifications for ALL vehicles
        basicPlanApplied = 'Yes'
        for vehicle in self.policy.vehicles:
            if vehicle.derivedData['BasicPlanQualified'] == 'No':
                basicPlanApplied = 'No'
        self.derivedData['BasicPlanApplied'] = basicPlanApplied
        
class premiumPart:
    def __init__(self, partType, vehicle, policy, inputs):
        self.partType = partType #part is an int from 1 to 12
        self.vehicle = vehicle
        self.policy = policy
        
        
    #helpers
    def roundingByPart(self, data):
        #Rounding!  Rounding is exactly defined by the manual and thus regulated.
        #A standard round(x,0) call should round x.5 and above up always.  Will need to verify if the built in round functions do that (frex, python built in round is different)
        #most rounding done is standard round(x,0), but part 5 and part 6 use floor in specific cases
        if self.partType in [1, 2, 3, 4, 7, 8, 9, 10, 11, 12]:
            return round(data, 0)
        elif self.partType == 5:
            if self.vehicle.coverages['Part5'] == '$20/40':
                return floor(data)
            else:
                return round(data, 0)
        elif self.partType == 6:
            if self.vehicle.coverages['Part6'] == '$5000':
                return floor(data)
            else:
                return round(data, 0)
        else:
            raise InvalidPartType()
    
    =IF($E$39="Trailer"
            ,0
            ,VLOOKUP($E$64,IF($E$16="A",Part1ABase_tbl,Part1BBase_tbl),MATCH(INDEX($E$28:$H$28,MATCH($E$5,$E$20:$H$20)),IF($E$16="A",BaseA_row,BaseB_row),0),FALSE)
            )
    
    =ROUND(IF($E$39="Trailer"
                ,IF($E$47="Yes"
                        ,0.5*VLOOKUP(1,IF($E$16="A",Part7ABase_tbl,Part7BBase_tbl),MATCH(IF($E$16="A",53,10),IF($E$16="A",BaseA_row,BaseB_row),0),FALSE)
                        ,0
                        )
                ,IF($E$47="Yes"
                        ,VLOOKUP($E$64,IF($E$16="A",Part7ABase_tbl,Part7BBase_tbl),MATCH(INDEX($E$28:$H$28,MATCH($E$5,$E$20:$H$20)),IF($E$16="A",BaseA_row,BaseB_row),0),FALSE)
                        ,0
                        )*IF($E$39="Pick-Up",0.6,1)
                )
            ,0
            )
    
    =ROUND(IF($E$49="Yes"
                ,IF($E$39="Trailer"
                    ,0.5*VLOOKUP(1,IF($E$16="A",Part9ABase_tbl,Part9BBase_tbl),MATCH(IF($E$16="A",53,10),IF($E$16="A",BaseA_row,BaseB_row),0),FALSE)
                    ,VLOOKUP($E$64,IF($E$16="A",Part9ABase_tbl,Part9BBase_tbl),MATCH(INDEX($E$28:$H$28,MATCH($E$5,$E$20:$H$20)),IF($E$16="A",BaseA_row,BaseB_row),0),FALSE)*IF($E$39="Pick-Up",0.9,1)
                    )
                ,0
                )
            ,0
            )
    #premium components.  Generally calculated from previous premium pieces, logic pivots off vehicle, driver, inputs values
    def baseRate(self):
        #setting up some initial checks just to keep the if/elif/else chain clean
        isTrailer           = True if self.vehicle.inputs['VehicleType'] == 'Trailer' else False
        isPickup            = True if self.vehicle.inputs['VehicleType'] == 'Pick-Up' else False
        hasCollision        = True if self.vehicle.coverages['Part7'] == 'Yes' else False
        hasComprehensive    = True if self.vehicle.coverages['Part9'] == 'Yes' else False

        #the Base rate lookup tables should be unpivoted into a 4 column lookup:
        #lookup_BaseRateTable(part, ratingPlan, territory, operatorClass) = {'rate': <value>}
        if isTrailer:
            if self.partType in (1,2,3,4,5,6,8,10,11,12):
                return 0
            elif () self.partType == 7 and hasCollision ) or ( self.partType == 9 and hasComprehensive ):
                baseRate = lookup_BaseRateTable(part=self.partType
                                                , ratingPlan = self.policy.derivedData['RatingPlan']
                                                , territory = self.vehicle.inputs['ratingTerritory']
                                                , operatorClass = self.vehicle.assignedDriver.derivedData['OperatorClass'][self.vehicle.vehicleId])
                return round(baseRate['rate'] * 0.5,0)
            elif 
        else:
            
                
    def yearsLicensedRSF(self):
        result = lookup_YearsLicensedRSFTable(yearsLicensed=self.vehicle.assignedDriver.inputs['YearsLicensed'])
        
        return result['RiskScoreFactor']
    
    def subTotalBeforeDiscounts(self):
    
    def subTotalAfterAntiTheft(self):
        if self.partType == 9:
            if self.policy.derivedData['RatingPlan'] == 'A':
                result = lookup_AntiTheftTable(antiTheftType=self.vehicle.inputs['AntiTheftDevice'])
                
                self.derivedData['AntiTheftDiscount'] = result['Discount']
            else:
                self.derivedData['AntiTheftDiscount'] = 1
        
            return self.roundingByPart(self.subTotalAfterMultiCar() * self.derivedData['AntiTheftDiscount'])
        else:
            return self.subTotalAfterMultiCar()
    
    def subTotalAfterLowFrequency(self):
        self.derivedData['LowFrequencyFactor'] = 0.9 if self.vehicle.derivedData['LowFrequency'] = 'Yes' else 1
        if self.partType in (1,2,4,5):
            return self.roundingByPart(self.subTotalAfterAntiTheft() * self.derivedData['LowFrequencyFactor'])
        else:
            return self.subTotalAfterAntiTheft()
            
    def basicPackageAdjFactor(self):

        #basic package table should be:
        #lookup_BasicPackageTable(garagingTown,operatorClass,meritRating,tier) = {'BasicPackageAdjustment': 0,657}
        if self.partType in (1,2,3,4,12):
            if self.vehicle.derivedData['BasicPlanApplied'] == 'Yes':
                yearsLicensedRSF = self.yearsLicensedRSF() if self.yearsLicensedRSF() > 1 else 1
                garagingTown='All'
                tier='All'
                operatorClass = self.vehicle.assignedDriver.derivedData['OperatorClass'][self.vehicle.vehicleId]
                meritRating = self.vehicle.assignedDriver.inputs['MeritRatingPoints']
                basicPackage = lookup_BasicPackageTable(garagingTown=garagingTown,operatorClass=operatorClass,meritRating=meritRating,tier=tier)
                
                if result is not None: #This check is in the formula, I'm assuming that the table does not cover all combinations, so a lookup fail is possible
                    self.derivedData['BasicPackageAdjustment'] = result['BasicPackageAdjustment'] / yearsLicensedRSF
                else:   
                    self.derivedData['BasicPackageAdjustment'] = 1
        else:
            self.derivedData['BasicPackageAdjustment'] =  1
        
        return self.derivedData['BasicPackageAdjustment']

    def age65OlderDiscount(self):
        if self.vehicle.assignedDriver.inputs['DriverAge'] > 64 or self.vehicle.assignedDriver.inputs['DriverAge'] == 15:
            self.derivedData['age65OlderDiscount'] = 0.75
        else:
            self.derivedData['age65OlderDiscount'] = 1
        
        return self.derivedData['age65OlderDiscount']        
    
    def subTotalRatingPlanB(self):
        if self.policy.derivedData['RatingPlan'] == 'B':
            return self.roundingByPart(self.subTotalAfterLowFrequency() * self.age65OlderDiscount())
        else:
            raise InvalidRatingPlan('subTotalRatingPlanB is only valid for rating plan B')
        
    def combinedDiscountFactor(self):
        #renewal
        if self.policy.inputs['RenewalCredit'] == 0:
            self.derivedData['RenewalDiscount'] = 1
        elif self.policy.inputs['RenewalCredit'] in (1,2,3):
            self.derivedData['RenewalDiscount'] = 0.99
        elif self.policy.inputs['RenewalCredit'] in (4,5):
            self.derivedData['RenewalDiscount'] = 0.98
        elif self.policy.inputs['RenewalCredit'] in (6,7,8,9,10):
            self.derivedData['RenewalDiscount'] = 0.97
        else:
            self.derivedData['RenewalDiscount'] = 0.96
        
        #student
        if self.vehicle.assignedDriver.derivedData['DriverGoodStudentDiscount'] == 'No' and  self.vehicle.assignedDriver.derivedData['DriverAwayStudentDiscount'] == 'No':
            self.derivedData['StudentDiscount'] = 1
        elif self.vehicle.assignedDriver.derivedData['DriverGoodStudentDiscount'] == 'Yes' and  self.vehicle.assignedDriver.derivedData['DriverAwayStudentDiscount'] == 'No':
            self.derivedData['StudentDiscount'] = 0.9
        elif self.vehicle.assignedDriver.derivedData['DriverGoodStudentDiscount'] == 'No' and  self.vehicle.assignedDriver.derivedData['DriverAwayStudentDiscount'] == 'Yes':
            self.derivedData['StudentDiscount'] = 0.9
        elif self.vehicle.assignedDriver.derivedData['DriverGoodStudentDiscount'] == 'Yes' and  self.vehicle.assignedDriver.derivedData['DriverAwayStudentDiscount'] == 'Yes':
            self.derivedData['StudentDiscount'] = 0.8
        else:
            self.derivedData['StudentDiscount'] = 1
        
        #ecustomer:
        #Ecustomer_tbl should be refactored into a 2 column index:
        #lookup_ecustomerTable(ecustomerYears,multiCarType)
        #ecustomerYears: 1-4, but if the i put value > 4, then use the 4 row
        #multiCarType: values in Ecustomer_row
        ecustomerYears = 3 if self.policy.inputs['YearsAsEcustomer'] > 3 else self.policy.inputs['YearsAsEcustomer']        
        result = lookup_ecustomerTable(ecustomerYears=ecustomerYears
                                        , multiCarType=self.policy.derivedData['MultiCarType'])
        self.derivedData['EcustomerDiscount'] = result['discountFactor']
        
        #electronic book transfer
        #The electron boko transfer discount 
        #ElectronicBook_tbl again refactored into:
        #lookup_ElectronicBookTable(yearsWithCompany, tierScoreBand)
        if self.policy.inputs['ElectronicBookTransfer'] == 'Yes':
            if self.policy.inputs['RenewalCredit'] == 0:
                self.derivedData['ElectronicBookDiscount'] = 0.89
            else:
                if self.policy.inputs['PreviousYearElectronicBookDiscount'] < 1
                    yearsWithCompany = 8 if self.policy.inputs['YearsWithCompany'] > 8 else self.policy.inputs['YearsWithCompany']
                    electronicBookAdjustment = lookup_ElectronicBookTable(yearsWithCompany=yearsWithCompany, tierScoreBand=self.policy.derivedData['TierScoreBand'])
                    if self.policy.inputs['PreviousYearElectronicBookDiscount'] + electronicBookAdjustment['discountFactor']
                        self.derivedData['ElectronicBookDiscount'] = 1
                    else:
                        self.derivedData['ElectronicBookDiscount'] = self.policy.inputs['PreviousYearElectronicBookDiscount'] + electronicBookAdjustment['discountFactor']
                else:
                    self.derivedData['ElectronicBookDiscount'] = 1
        else:
            self.derivedData['ElectronicBookDiscount'] = 1
        
        #accountCredit
        self.derivedData['AccountCreditDiscount'] = 0.95 if self.policy.inputs['AccountCredit'] == 'Yes' else 1
        
        #example of the early issuance lookup formula in tne excel
        # =IF($E$113="Yes"
            # ,IF($E$96=0
                # ,0.89
                # ,IF($E$115<1
                    # ,IF($E$115+VLOOKUP($E$34,EarlyIssuance_tbl,MATCH($E$15,EarlyIssuance_row,0),TRUE)>1
                        # ,1
                        # ,$E$115+VLOOKUP($E$34,EarlyIssuance_tbl,MATCH($E$15,EarlyIssuance_row,0),TRUE)
                        # )
                    # ,1
                    # )
                # )
            # ,1
            # )
        
        #early issuance
        #Early issuance discount is a declining discount.  Each year the discount is reduced (moved closer to 1) by the value in the EarlyIssuance_tbl
        #EarlyIssuance_tbl should be refactored the same as ElectronicBook_tbl        
        #lookup_EarlyIssuanceTable(yearsWithCompany, tierScoreBand)
        if self.policy.inputs['EarlyIssuance'] =='Yes':
            if self.policy.inputs['RenewalCredit'] == 0:
                self.derivedData['EarlyIssuanceDiscount'] = 0.89
            else:
                if self.policy.inputs['PreviousYearEarlyIssuanceDiscount'] < 1:
                    yearsWithCompany = 8 if self.policy.inputs['YearsWithCompany'] > 8 else self.policy.inputs['YearsWithCompany']
                    earlyIssuanceAdjustment = lookup_EarlyIssuanceTable(yearsWithCompany=yearsWithCompany, tierScoreBand=self.policy.derivedData['TierScoreBand'])
                    if self.policy.inputs['PreviousYearEarlyIssuanceDiscount'] + earlyIssuanceAdjustment['discountFactor'] > 1:
                        self.derivedData['EarlyIssuanceDiscount'] = 1
                    else:
                        self.derivedData['EarlyIssuanceDiscount'] = self.policy.inputs['PreviousYearEarlyIssuanceDiscount'] + earlyIssuanceAdjustment['discountFactor']
                else:
                    self.derivedData['EarlyIssuanceDiscount'] = 1
        else:
            self.derivedData['EarlyIssuanceDiscount'] = 1
        
        self.derivedData['combinedDiscountFactor'] = self.derivedData['RenewalDiscount'] * self.derivedData['StudentDiscount'] * self.derivedData['EcustomerDiscount'] * self.derivedData['ElectronicBookDiscount'] * self.derivedData['AccountCreditDiscount'] * self.derivedData['EarlyIssuanceDiscount'] * self.derivedData['age65OlderDiscount']

        return self.derivedData['combinedDiscountFactor']
            
    def adjustedDiscountFactor(self):
        return .065 if self.combinedDiscountFactor() < 0.65 else self.combinedDiscountFactor()
        
    def premiumAfterDiscounts(self):
        if self.policy['RatingPlan'] == 'B':
            return self.subTotalRatingPlanB()
        else:
            if self.partType in (1,2,3,4,12):
                premiumAfterDiscounts = self.subTotalAfterAntiTheft() * self.basicPackageAdjFactor() * self.adjustedDiscountFactor()
            else:
                premiumAfterDiscounts = self.subTotalAfterAntiTheft() * self.adjustedDiscountFactor()
            
            return self.roundingByPart(premiumAfterDiscounts)
            
    def meritRatingAdjustment(self):
        if self.partType in (3,6,8,9,10,11,12):
            return 1 #these parts have no merit rating adjustment
        elif self.partType in (1,2,4,5,7):
            #note this lookup is not exactly how the MeritA_tbl and MeritB_tbl are defined in the excel on Supplemental.  Looking at the structure, we can redesign slightly to lookup properly:
            #lookup_MeritRatingTable[ratingTable][meritRatingPoints][operatorClassType][part] ==> {'meritRatingAdjustment': <data>}
            # ratingTable: A/B
            # meritRatingPoints: 0-45, 98, 99 (not sure if this is a static set or open for expansion)
            # operatorClassType: Experienced/Inexperienced
            # part: 1,2,4,5,7
            result = lookup_MeritRatingTable(ratingTable=self.policy.derivedData['RatingPlan']
                                                , meritRatingPoints=self.vehicle.assignedDriver.inputs['MeritRatingPoints']
                                                , operatorClassType=self.vehicle.assignedDriver.derivedData['OperatorClassType'][self.vehicle.vehicleId]
                                                , part=self.partType)
            
            return result['meritRatingAdjustment']
        else:
            raise InvalidPartType()
        
    def premiumAfterMeritRating(self):
        if self.vehicle.inputs['useOfOtherAutos'] == 'Yes' or self.vehicle.inputs['namedNonOwnerPolicy'] == 'Yes':
            premiumAfterMeritRating = self.meritRatingAdjustment() * self.subTotalBeforeDiscounts()
        else:
            premiumAfterMeritRating = self.meritRatingAdjustment() * self.premiumAfterDiscounts()
        
        return self.roundingByPart(premiumAfterMeritRating)
    
    def premiumAfterPolicyPeriod(self):
        if self.policy.inputs['PolicyPeriod'] == 'Annual':
            premiumAfterPolicyPeriod = self.premiumAfterMeritRating()
        elif self.policy.inputs['PolicyPeriod'] == 'Semiannual':
            premiumAfterPolicyPeriod = self.premiumAfterMeritRating() * 0.5
        else:
            raise InvalidPremiumPeriod()
            
        return self.roundingByPart(premiumAfterPolicyPeriod)
     
    def transportNetworkDriverCoveragePremium(self):    
        
        transportNetworkDriverCoveragePremium = 0.1 * self.premiumAfterPolicyPeriod() if self.vehicle.inputs['transportNetworkDriverCoverage'] == 'Yes' else 0
        
        return self.roundingByPart(transportNetworkDriverCoveragePremium)
            
    def totalPremium(self):
        return self.premiumAfterPolicyPeriod() + self.transportNetworkDriverCoveragePremium()
