@isTest
private class WsMockVehicleTest {
    
    private static testmethod void getFuelTypeTest(){
        Test.startTest();
        BackEndRequest_m backE = new BackEndRequest_m();
        backE.setInputData('OptionParams', new Map<String, Object>{'EnumId'=>'test'});
        backE = WsMockVehicle.getFuelType(backE);
        System.assert(backE.isSuccess());
        Test.stopTest();
    }
    
    private static testmethod void VehicleMarkFindTest(){
        Test.startTest();
        BackEndRequest_m backE = new BackEndRequest_m();
        backE = WsMockVehicle.VehicleMarkFind(backE);
        System.assert(backE.isSuccess());
        Test.stopTest();
    }
    
    @isTest//(SeeAllData=true)
    private static void VehicleModelFindTest(){
        Test.startTest();
        BackEndRequest_m backE = new BackEndRequest_m();
        backE.setInputData('OptionParams', new Map<String, Object>{'Mark'=>'MERCEDES'});
        backE = WsMockVehicle.VehicleModelFind(backE);
        System.assert(backE.isSuccess());
        Test.stopTest();
    }
    
    @isTest//(SeeAllData=true)
    private static void getVehicleByDescriptionTest(){
        Test.startTest();
        BackEndRequest_m backE = new BackEndRequest_m();
        Vehicle_m vehicleM = new Vehicle_m(); vehicleM.initSFObject();
        vehicleM.SFObject.Mark__c = 'MERCEDES';
        vehicleM.SFObject.Model__c = '240';
        backE.setInputData('OptionParams', new Map<String, Object>{'vehicleM'=>vehicleM});
        backE = WsMockVehicle.getVehicleByDescription(backE);
        System.assert(backE.isSuccess());
        Test.stopTest();
    }
    
    private static testmethod void createVehicleRiskTest(){
        Test.startTest();
        BackEndRequest_m backE = new BackEndRequest_m();
        backE.BackEndName_m = 'MOCKUP';
        Type ClassBackEnd = Type.forName('BackEnd'+backE.BackEndName_m);
        backE.BackEndInterface = (BackEndInterface)ClassBackEnd.newInstance();

        Vehicle_m vehicleM = new Vehicle_m(); 
        vehicleM.initSFObject();

        Risk_m riskM = new Risk_m(); 
        riskM.initSFObject();
        riskM.SFObject.Vehicle__r = vehicleM.SFObject;

        InsuranceContract_m contractM = new InsuranceContract_m(); 
        contractM.initSFObject();
        contractM.SFObject.URI__c = 'baseURI';
        contractM.RiskList_m = new List<Risk_m>{riskM};

        Case_m caseM = new Case_m(); 
        caseM.initSFObject();
        caseM.SFObject.InputData__c = JSON.serialize(new Map<String, Object>{'insuranceContractM'=>contractM});
        backE.setInputData('caseM', caseM);
        backE = WsMockVehicle.createVehicleRisk(backE);
        System.assert(backE.isSuccess());

        InsuranceQuote_m quoteM = new InsuranceQuote_m(); 
        quoteM.initSFObject();
        quoteM.SFObject.URI__c = 'baseURI';
        quoteM.RiskList_m = new List<Risk_m>{riskM};
        caseM.SFObject.InputData__c = JSON.serialize(new Map<String, Object>{'insuranceQuoteM'=>quoteM});
        backE.setInputData('caseM', caseM);
        backE = WsMockVehicle.createVehicleRisk(backE);
        System.assert(backE.isSuccess());
        Test.stopTest();
    }
    
    private static testmethod void createVehicleDriverTest(){
        Test.startTest();
        BackEndRequest_m backE = new BackEndRequest_m();
        Vehicle_m vehicleM = new Vehicle_m(); vehicleM.initSFObject();
        Risk_m riskM = new Risk_m(); riskM.initSFObject();
        Person_m driver = new Person_m(); driver.initSFObject();
        List<Person_m> driverList = new List<Person_m>{driver};
        riskM.SFObject.Vehicle__r = vehicleM.SFObject;
        VehicleDriver_m vDriver = new VehicleDriver_m(); vDriver.initSFObject();
        vDriver.SFObject.RelatedAccount__r = driver.SFObject;
        List<VehicleDriver_m> vehicleDriverList = new List<VehicleDriver_m>{vDriver};
            vehicleM.VehicleDriverList_m = vehicleDriverList;
        riskM.VehicleM = vehicleM;
            InsuranceContract_m contractM = new InsuranceContract_m(); contractM.initSFObject();
        contractM.SFObject.URI__c = 'baseURI';
        contractM.RiskList_m = new List<Risk_m>{riskM};
            Case_m caseM = new Case_m(); caseM.initSFObject();
        caseM.SFObject.InputData__c = JSON.serialize(new Map<String, Object>{'insuranceContractM'=>contractM, 'vehicleDriverList'=>vehicleDriverList, 'driverList'=>driverList});
        backE.setInputData('caseM', caseM);
        backE = WsMockVehicle.createVehicleDriver(backE);
        System.assert(backE.isSuccess());
        InsuranceQuote_m quoteM = new InsuranceQuote_m(); quoteM.initSFObject();
        quoteM.SFObject.URI__c = 'baseURI';
        quoteM.RiskList_m = new List<Risk_m>{riskM};
            caseM.SFObject.InputData__c = JSON.serialize(new Map<String, Object>{'insuranceQuoteM'=>quoteM, 'vehicleDriverList'=>vehicleDriverList, 'driverList'=>driverList});
        backE.setInputData('caseM', caseM);
        backE = WsMockVehicle.createVehicleDriver(backE);
        System.assert(backE.isSuccess());
        Test.stopTest();
    }
}