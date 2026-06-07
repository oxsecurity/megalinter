*** Settings ***
Library    Collections    WITH NAME    AliasedName

*** Keywords ***
My Amazing Keyword
    [Arguments]    ${argument_name}=    ${first_arg}=

*** Test Cases ***
Valid Login
    Open Login Page
    Input Username    demo
    Input Password    mode
    Submit Credentials
    Welcome Page Should Be Open

Setting Variables
    Do Something    first argument    second argument
    ${value} =    Get Some Value
    Should Be Equal    ${value}    Expected value
