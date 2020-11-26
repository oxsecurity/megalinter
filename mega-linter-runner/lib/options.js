/**
 * @fileoverview Options configuration for optionator.
 * @author Nicolas Vuillamy
 */

"use strict";

//------------------------------------------------------------------------------
// Requirements
//------------------------------------------------------------------------------

const optionator = require("optionator");

//------------------------------------------------------------------------------
// Initialization and Public Interface
//------------------------------------------------------------------------------

// exports "parse(args)", "generateHelp()", and "generateHelpForOption(optionName)"
module.exports = optionator({
    prepend: "mega-linter [options]",
    defaults: {
        concatRepeatedArrays: true,
        mergeRepeatedObjects: true
    },
    options: [
        {
            option: "release",
            alias: "r",
            type: "String",
            default: "v4",
            description: "Mega-Linter version",
            example: ["stable", "latest", "v4.9.0"]
        },
        {
            option: "path",
            alias: "p",
            type: "path::String",
            default: ".",
            description: "Directory containing the files to lint (default: current directory)",
            example: ["./path/to/my/files"]
        },
        {
            option: "fix",
            type: "Boolean",
            description: "Apply formatters and fixes in linted sources"
        },
        {
            option: "nodockerpull",
            type: "Boolean",
            description: "Do not pull docker image before running it"
        },
        {
            option: "debug",
            type: "Boolean",
            description: "See debug logs"
        },
        {
            option: "help",
            alias: "h",
            type: "Boolean",
            description: "Show help (mega-linter --help OPTIONNAME to see option detail)"
        },
        {
            option: "version",
            alias: "v",
            type: "Boolean",
            description: "Show version"
        }
    ],
    mutuallyExclusive: [
        ["help", "version"]
    ]
});
