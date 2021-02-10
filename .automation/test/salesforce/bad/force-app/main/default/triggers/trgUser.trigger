trigger trgUser on User (before insert, before update) {
    System.debug(LoggingLevel.DEBUG,'Entering trgUser (trigger on User before insert,  before update)') ;
    
    String BaseURI = UtilsURI.getSFDCBaseURI();
    for(User userC : trigger.New) {
        // Manage URI
        String URI = BaseURI + '/users/'+userC.Username ;
        if (trigger.isBefore && userC.URI__c == null || userC.URI__c != URI) {
        	userC.URI__c = URI  ;
            System.debug(LoggingLevel.INFO,'Trigger: updated user URI for user: '+userC) ;
        }
        // Manage ProfileId ( SFDC bug https://salesforce.stackexchange.com/questions/156187/system-dmlexception-insert-failed-required-fields-are-missing-profile?rq=1 )
        if (trigger.isBefore && userC.ProfileId == null && userC.StayInTouchSubject != null && UtilsApex.isValidSFDCId(userC.StayInTouchSubject)) {
            userC.ProfileId = Id.valueOf(userC.StayInTouchSubject);
            userC.StayInTouchSubject = null ;
        }
    }

}
