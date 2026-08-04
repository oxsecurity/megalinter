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
    *** Test Cases ***
Test
    FOR    ${x}    IN    foo    bar
        Log    ${x}

Setting Variables
    [Documentation]    Test documentation
    Do Something    first argument    second argument
    ${value} =    Get Some Value
    Should Be Equal    ${value}    Expected value
