public class WsMockVehicle {
    
    public static BackEndRequest_m VehicleMarkFind(BackEndRequest_m BackEndRequestM){
        Map<String,String> MarksMap = new Map<String,String>(); 
        String JSONStr = null;
        
        JSONStr = WsMockServ.ResourceJSONGet('Vehicle_m');
        Map<String, Object> MarksMapTemp = (Map<String, Object>)JSON.deserializeUntyped(JSONStr);
        
        Set <String> MarksSet = new Set<String>(); 
        MarksSet = MarksMapTemp.keySet();
        
        for (String Mark : MarksSet){
            MarksMap.put(Mark,Mark);
        }
        
        BackEndRequestM.setOutputData('ResultList', MarksMap); 
        BackEndRequestM.setSuccess();
        
        return BackEndRequestM;  
    }
    
    public static BackEndRequest_m VehicleModelFind(BackEndRequest_m BackEndRequestM){
        Map<String,String> ModelsMap = new Map<String,String>();  
        
        Map<String,Object> InputOptionParams = (Map<String,Object>)BackEndRequestM.getInputData('OptionParams') ; 
        String VehicleMark = (String)InputOptionParams.get('Mark');
        String JSONStr = null;
        
        JSONStr = WsMockServ.ResourceJSONGet('Vehicle_m');
        Map<String, Object> MarksMap = (Map<String, Object>)JSON.deserializeUntyped(JSONStr);
        Map<String, Object> ModelsMapTemp = (Map<String, Object>)MarksMap.get(VehicleMark);
        
        Set <String> ModelsSet = new Set<String>(); 
        ModelsSet = ModelsMapTemp.keySet();
        
        for (String Model : ModelsSet){
            ModelsMap.put(Model,Model);
        }
        
        BackEndRequestM.setOutputData('ResultList', ModelsMap); 
        BackEndRequestM.setSuccess();
        
        return BackEndRequestM;  
    }
    
    public static BackEndRequest_m getVehicleByDescription(BackEndRequest_m BackEndRequestM){
        Map<String,String> ResultList = new map<String, String>();
        Map<String,Map<String, String>> vehicleDescList = new map<String, Map<String, String>>();
        Map<String,Object> OptionParams = (Map<String,Object>)BackEndRequestM.getInputData('OptionParams') ;
        Vehicle_m vehicleM = (Vehicle_m)JSON.deserialize(JSON.serialize(OptionParams.get('vehicleM')), Vehicle_m.class);
        
        String JSONStr = null;
        
        JSONStr = WsMockServ.ResourceJSONGet('Vehicle_m');
        Map<String, Object> MarksMap = (Map<String, Object>)JSON.deserializeUntyped(JSONStr);
        Map<String, Object> ModelsMap = (Map<String, Object>)MarksMap.get(vehicleM.SFObject.Mark__c);
        Map<String, Object> VersionsMap = (Map<String, Object>)ModelsMap.get(vehicleM.SFObject.Model__c);
        
        Set <String> VersionsSet = new Set<String>(); 
        VersionsSet = VersionsMap.keySet();
        
        for (String Version : VersionsSet){
            Map<String, Object> VehicleMap = (Map<String, Object>)VersionsMap.get(Version);
            Map<String, Object> Vehicle = (Map<String, Object>)VehicleMap.get('SFObject');
            String cubicCapacity = (String)Vehicle.get('CubicCapacity__c');
            String power = (String)Vehicle.get('Power__c');
            vehicleDescList.put(Version, new Map<String, String>{'power' => power, 'cubicCapacity' => cubicCapacity});
            ResultList.put(Version,Version);
        }
        
        BackEndRequestM.setOutputData('vehicleDescList', vehicleDescList);
        BackEndRequestM.setOutputData('ResultList', ResultList);
        BackEndRequestM.setSuccess();
        
        return BackEndRequestM;  
    }    
    
    public static BackEndRequest_m createVehicleRisk(BackEndRequest_m BackEndRequestM){
        //retrieve InsuranceQuote_m or InsuranceContract_m and vehicleList
        InsuranceObjectRoot_m InsuranceObjectM = SrvcAutoNewBusiness.getInsuranceObject(BackEndRequestM);
        String InsuranceObjectURI = SrvcAutoNewBusiness.getSFField(InsuranceObjectM, 'URI__c');
        String BaseURI = BackEndRequestM.getBackEndInterface().getBaseURI();
        List<Risk_m> riskList = SrvcAutoNewBusiness.getRiskList(InsuranceObjectM);
        for(Integer i=0; i<riskList.size(); i++){
            riskList[i].SFObject.URI__c = InsuranceObjectURI + '/risks/' + String.valueOf(i);
            riskList[i].SFObject.Vehicle__r.URI__c = UtilsURI.BuildURI(BaseURI,'/vehicle/',String.valueOf(Math.random()));
        }
        if(InsuranceObjectM.getSObjectType() == ns.add('InsuranceContract__c')){
            InsuranceContract_m InsuranceContractM = new InsuranceContract_m();
            InsuranceContractM = (InsuranceContract_m)InsuranceObjectM;
            InsuranceContractM.RiskList_m = riskList;
            BackEndRequestM.setCaseInputData('insuranceContractM', InsuranceContractM);
        }

        else if (InsuranceObjectM.getSObjectType() == ns.add('InsuranceQuote__c')){
            InsuranceQuote_m InsuranceQuoteM = new InsuranceQuote_m();
            InsuranceQuoteM = (InsuranceQuote_m)InsuranceObjectM;
            InsuranceQuoteM.RiskList_m = riskList;
            BackEndRequestM.setCaseInputData('insuranceQuoteM', InsuranceQuoteM);
        }
        else 
            BackEndRequestM.setError('ERROR: InsuranceQuote_m or InsuranceContract_m not found');
        
        BackEndRequestM.setSuccess();
        
        return BackEndRequestM;
    }
    
    public static BackEndRequest_m createVehicleDriver(BackEndRequest_m BackEndRequestM){
        //retrieve InsuranceQuote_m or InsuranceContract and vehicleList
        Case_m CaseM = (Case_m)BackEndRequestM.getInputData('caseM') ;
        InsuranceObjectRoot_m InsuranceObjectM = SrvcAutoNewBusiness.getInsuranceObject(BackEndRequestM);
        String BaseURI = SrvcAutoNewBusiness.getSFField(InsuranceObjectM, 'URI__c');
        list<VehicleDriver_m> vehicleDriverList = (list<VehicleDriver_m>)JSON.deserialize(JSON.serialize(CaseM.getCaseInputData('vehicleDriverList')),list<VehicleDriver_m>.class);
        for (Integer i=0; i<vehicleDriverList.size(); i++){
            if (vehicleDriverList[i].SFObject.URI__c == null)
                vehicleDriverList[i].SFObject.URI__c = UtilsURI.BuildURI(BaseURI,'/vehicle_drivers/',String.valueOf(Math.random()));
        }
        list<Person_m> driverList = (list<Person_m>)JSON.deserialize(JSON.serialize(CaseM.getCaseInputData('driverList')),list<Person_m>.class);
        for (Integer i=0; i<driverList.size(); i++){
            if (driverList[i].SFObject.URI__c == null)
                driverList[i].SFObject.URI__c = UtilsURI.BuildURI(BaseURI,'/drivers/',String.valueOf(Math.random()));
        }
        List<Risk_m> RiskListM = SrvcAutoNewBusiness.getRiskList(InsuranceObjectM);
        for (Integer i=0; i<RiskListM.size(); i++){
            for (Integer j=0; j<RiskListM[i].VehicleM.VehicleDriverList_m.size(); j++){
                if (RiskListM[i].VehicleM.VehicleDriverList_m[j].SFObject.RelatedAccount__r.URI__c == null){
                    RiskListM[i].VehicleM.VehicleDriverList_m[j].SFObject.RelatedAccount__r.URI__c = UtilsURI.BuildURI(BaseURI,'/persons/',String.valueOf(Math.random()));
                }
            }
        }
        if (InsuranceObjectM.getSObjectType() == ns.add('InsuranceQuote__c')){
            InsuranceQuote_m InsuranceQuoteM = new InsuranceQuote_m();
            InsuranceQuoteM = (InsuranceQuote_m)InsuranceObjectM;
            InsuranceQuoteM.RiskList_m = RiskListM;
            BackEndRequestM.setCaseInputData('insuranceQuoteM', InsuranceQuoteM);
        }
        else if(InsuranceObjectM.getSObjectType() == ns.add('InsuranceContract__c')){
            InsuranceContract_m InsuranceContractM = new InsuranceContract_m();
            InsuranceContractM = (InsuranceContract_m)InsuranceObjectM;
            InsuranceContractM.RiskList_m = RiskListM;
            BackEndRequestM.setCaseInputData('insuranceContractM', InsuranceContractM);
        }
        else 
            BackEndRequestM.setError('ERROR: InsuranceQuote_m or InsuranceContract_m not found');
        
        BackEndRequestM.setSuccess();
        BackEndRequestM.setOutputData('vehicleDriverList',vehicleDriverList);
        BackEndRequestM.setOutputData('driverList',driverList);
        
        return BackEndRequestM;
    }
    
    public static BackEndRequest_m getFuelType(BackEndRequest_m BackEndRequestM)
    {
        Map<String,Object> OptionParams = (Map<String,Object>)BackEndRequestM.getInputData('OptionParams') ;
        String EnumId = (String)OptionParams.get('EnumId');
        Map<String,String> ResultList = UtilsApex.ListPickListValues(EnumId);
        
        BackEndRequestM.setOutputData('ResultList', ResultList);
        BackEndRequestM.setSuccess();
        
        return BackEndRequestM ;
    }
    
}
