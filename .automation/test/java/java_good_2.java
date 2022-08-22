package com.dummy.nico;

@SuppressWarnings({
  "checkstyle:hideutilityclassconstructor",
  "PMD.UseUtilityClass"
})
public class Application {

  /**
   * main.
   *
   * @param args
   */
  public static void main(final String[] args) {
    SpringApplication.run(Application.class, args);
  }

}
