# Each of the default linters should throw at least one lint on this file

# assignment
# function_left_parentheses
# brace_linter
# commas
# paren_brace
f = function (x,y = 1){}

# commented_code
# some <- commented("out code")

# cyclocomp
# equals_na
# brace_linter
# indentation
# infix_spaces
# line_length
# object_length
# object_name
# object_usage
# open_curly
# T_and_F_symbol
someComplicatedFunctionWithALongCamelCaseName <- function(x)
{
    y <- 1
  if (1 > 2 && 2 > 3 && 3 > 4 && 4 > 5 && 5*10 > 6 && 5 > 6 && 6 > 7 && x == NA) {T} else F
}

# vector_logic
if (1 & 2) FALSE else TRUE

# function_brace
my_metric <- function(x)
  sum(x) + prod(x)

# no_tab
# pipe_continuation
# seq_linter
# spaces_inside
# indentation
x <- 1:10
x[ 2]
1:length(x) %>% lapply(function(x) x*2) %>%
	head()

# single_quotes
message('single_quotes')

# spaces_left_parentheses
# trailing_whitespace
# semicolon
x <- 42; y <- 2 +(1:10) 

# trailing_blank_lines

