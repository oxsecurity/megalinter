public class SoqlInLoop {
    public static void main() {
        for (Integer i = 0; i < 10; i++) {
            List<Account> accounts = [SELECT Id FROM Account];
        }
    }
}
