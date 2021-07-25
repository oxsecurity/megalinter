trigger trgUser on User (before insert, before update) {
    SomeTriggerClass.process(trigger.New);
}
