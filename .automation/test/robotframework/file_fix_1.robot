*** Settings ***
Documentation       Suite documentation


*** Test Cases ***
Valid Login
    [Documentation]    Test documentation
    Open Login Page
    Input Username    demo
    Input Password    mode
    Submit Credentials
    Welcome Page Should Be Open

Setting Variables
    [Documentation]    Test documentation
    Do Something    first argument    second argument
    ${value} =    Get Some Value
    Should Be Equal    ${value}    Expected value
