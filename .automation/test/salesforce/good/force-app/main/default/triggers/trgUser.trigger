trigger trgUser on User (before insert, before update) {
    System.debug(LoggingLevel.DEBUG,'Entering trgUser (trigger on User before insert,  before update)') ;
    SomeTriggerClass.process(trigger.New);
}