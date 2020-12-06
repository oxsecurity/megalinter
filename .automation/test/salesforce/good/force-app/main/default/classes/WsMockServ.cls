// ISV PACKAGED
global with sharing class WsMockServ {
    
    global static BackEndRequest_m ManageResultBackEndRequestM(BackEndRequest_m BackEndRequestM, Object objInsurance, String resultType)
    {
        if (objInsurance != null)
        {
            BackEndRequestM.setSuccess(); 
            // Result type is Result List or simple Result
            BackEndRequestM.setOutputData(resultType, objInsurance);
        }
		
        return BackEndRequestM;
    }
    
    global static String ResourceJSONGet(String DecoratorClass)
    {
        String NameResourceJSON = 'mockData_' + DecoratorClass;
        String JSONResult;
		
        // WsMockServ class not used in production, that's why verify rights isn't a security vulnerability
		//UtilsSOQL.testFieldsAccessible('StaticResource', new list<String>{'Id','Body'});
        List<StaticResource> sr = [SELECT Id, Body FROM StaticResource WHERE Name =: NameResourceJSON ORDER BY CreatedDate desc LIMIT 1];
        if (sr.size() > 0) {
            String JSONstr = sr[0].Body.toString();
        	JSONResult = replaceRecordtyId(JSONstr);
        }
		
        return JSONResult;
    }
    
    global static InsuranceObjectRoot_m BuildMockGetResults(BackEndRequest_m BackEndRequestM, List<InsuranceObjectRoot_m> objInsurance) {

        UtilsApex.systemDebugObject(BackEndRequestM);
        
        InsuranceObjectRoot_m Result = new InsuranceObjectRoot_m();
        String requestURI = (String)BackEndRequestM.getInputData('Identifier');
        Boolean foundResult = false ;

        for (InsuranceObjectRoot_m obj : objInsurance) {
            String objURI = (String)obj.getSFObject().get(ns.add('URI__c'));
			system.debug('URI : '+objURI);
            system.debug('requestURI : '+requestURI);
            if (objURI == requestURI){
                Result = obj;
                foundResult = true ;
            }
        }
        
        if (foundResult == true)
            return Result;
        else
            return null;
    }
   
    global static List<InsuranceObjectRoot_m> BuildMockFindResults(BackEndRequest_m BackEndRequestM, List<InsuranceObjectRoot_m> objInsurance)
    {
        List<SearchCriteria> CritLs = (List<SearchCriteria>)BackEndRequestM.getInputData('CritLs');
        List<InsuranceObjectRoot_m> ResultList = new List<InsuranceObjectRoot_m>();
        Boolean CritMatch = true;
        
        for (InsuranceObjectRoot_m obj : objInsurance) {
            for (SearchCriteria Crit : CritLs)
            {
                String objValue;
                Date objValueDate;
                
                // For now, we ignore search criteria that use innerObj (joint between table) in Mock
                if (Crit.innerObj != null) {
                    continue ;
                }

                String CritField = Crit.Field;
                if (CritField.contains('date'))
                    objValueDate =  WsMockServ.getCritvalueDate(obj.getSFObject(), Crit.Field);                 
                else
                    objValue = WsMockServ.getCritvalue(obj.getSFObject(), Crit.Field);
                
                if (objValue == ''|| objValue == null || Crit.Value == null || objValue.containsIgnoreCase(Crit.Value.removeEnd('%')) == false)
                    CritMatch = false;
            }
            if(CritMatch)
                ResultList.add(obj);
            
            CritMatch = true;
        }
        
        return ResultList;
    }
    
    global static string replaceRecordtyId(String JSONstr){
        String JSONResult;
        JSONstr = JSONstr.replace(' : ', ':');
        JSONstr = JSONstr.replace(': ', ':');
        JSONstr = JSONstr.replace(' :', ':');
        Pattern patrn = Pattern.compile('"RecordTypeId":"([a-zA-Z].*?)"');
        Matcher matchr = patrn.matcher(JSONstr);
		
        // Automatically generated JSONs use the format below
        Id recordType;
        String recordTypeKey;
		
        While(matchr.find()) {
            String tmp = matchr.group(1);
            recordTypeKey = tmp.trim();
			
            if(recordTypeKey == 'RECORDTYPE_Person_m') {
                recordType = UtilsApex.getRecordTypeId ('Account', 'PersonAccount');
            } 
			else if(recordTypeKey == 'RECORDTYPE_Organization_m') {
                recordType = UtilsApex.getRecordTypeId ('Account', 'Business_Account');
            } 
			else if(recordTypeKey == 'RECORDTYPE_InsuranceContract_m') {
                recordType = UtilsApex.getRecordTypeId (ns.add('InsuranceContract__c'), 'InsurancePolicy');
            } 
			else if(recordTypeKey == 'RECORDTYPE_Questionnaire_m') {
                recordType = UtilsApex.getRecordTypeId (ns.add('Questionnaire__c'), 'InsuranceQuestionnaire');
            } 
			else if(recordTypeKey == 'RECORDTYPE_Question_m') {
                recordType = UtilsApex.getRecordTypeId (ns.add('Question__c'), 'InsuranceQuestion');
            } 
			else if(recordTypeKey == 'RECORDTYPE_QuestionAnswer_m') {
                recordType = UtilsApex.getRecordTypeId (ns.add('QuestionAnswer__c'), 'InsuranceQuestionAnswer');
            } 
			else if(recordTypeKey == 'RECORDTYPE_QuestionAnswerDefinition_m') {
                recordType = UtilsApex.getRecordTypeId (ns.add('QuestionAnswer__c'), 'InsuranceQuestionAnswerDefinition');
            } 
			else {
                String decoratorClassName = recordTypeKey.substringAfter('RECORDTYPE_');
                Type decoratorClass = Type.forName(decoratorClassName);
				
                if (decoratorClass != null) {
                    InsuranceObjectInterface_m descObj = (InsuranceObjectInterface_m)decoratorClass.newInstance();
                    descObj.initSFObject();
                    recordType = (Id)descObj.getSFObject().get('RecordTypeId');
                } 
				else if (recordTypeKey.contains('@')) {
                    recordType = UtilsApex.getRecordTypeId(recordTypeKey.substringBefore('@'),recordTypeKey.substringAfter('@'));
                }
                    
            }
			
            JSONstr = matchr.replaceFirst('"RecordTypeId" : "'+recordType+'"');
            matchr = patrn.matcher(JSONstr);
        }
		
        return JSONstr;
    }
    
    private static string getCritvalue(SObject obj, String CritField){
        String objValue;
        
        if (CritField.contains('.')){
            String SObjLink = CritField.substringBefore('.');
            SObject SObjLinkObj = obj.getSObject(SObjLink);
            
            if(SObjLinkObj == null){
                return null;
            }
            else if(CritField.substringAfter('.').contains('.')){
                return getCritvalue(SObjLinkObj, CritField.substringAfter('.'));
            }else {
                return objValue = (String)SObjLinkObj.get(CritField.substringAfter('.'));
            }
        }
        else {
            // this try is here for check if RecordTypeId is here or not
            try 
            { 
                objValue = (String)obj.get(CritField);
                objValue = objValue.toUpperCase(); 
            } 
			catch(Exception e) 
            {
                System.debug('RecordTypeId is not in this object maybe is on sub object ...');
            }
        }
        
        return objValue;
    }
    
    private static Date getCritvalueDate(SObject obj, String CritField){
        Date objValue;
        
        if (CritField.contains('.')){
            String SObjLink = CritField.substringBefore('.');
            SObject SObjLinkObj = obj.getSObject(SObjLink);
            
            if(SObjLinkObj == null){
                return null;
            }
            else if(CritField.substringAfter('.').contains('.')){
                return getCritvalueDate(SObjLinkObj, CritField.substringAfter('.'));
            }else {
                return objValue = (Date)SObjLinkObj.get(CritField.substringAfter('.'));
            }
        }
        else {
            // this try is here for check if RecordTypeId is here or not
            try { 
                objValue = (Date)obj.get(CritField);
            } 
			catch(Exception e) {
                System.debug('RecordTypeId is not in this object maybe is on sub object ...');
            }
        }
        
        return objValue;
    }
}