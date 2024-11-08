# This file has no lints

f <- function(x, y = 1) {

}
short_snake <- function(x) {
  y <- 1
  y <- y^2
  if (1 > 2 && 5 * 10 > 6 && is.na(x)) {
    TRUE
  } else {
    FALSE
  }
}

if (1 && 2) FALSE else TRUE

my_metric <- function(x) {
  sum(x) + prod(x)
}

x <- 1:10
x[2]
seq_len(x) %>%
  lapply(function(x) x * 2) %>%
  head()

message("single_quotes")

x <- 42
y <- 2 + (1:10)
