#! /usr/bin/env node
"use strict";
const glob = require("glob-promise");
const fs = require("fs-extra");
const path = require("path");
const c = require("chalk");
const prompts = require("prompts");
const { OXSecuritySetup } = require("./ox-setup");
const { asciiArt } = require("./ascii");
const { DEFAULT_RELEASE } = require("./config");

class CodeTotalRunner {
  constructor() {
  }

  async run() {
    console.log(asciiArt());
  }
}

module.exports = { CodeTotalRunner };
