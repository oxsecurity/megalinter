#! /usr/bin/env node
'use strict'
const { MegaLinterRunner } = require('../lib/index')
const assert = require('assert')

describe('Module', function () {
  it('(Module) run on own code base', async () => {
    const options = {
      path: './..',
      debug: true
    }
    const result = await new MegaLinterRunner().run(options)
    assert(process.exitCode === 0, `process.exitCode is 0 (${process.exitCode} returned)`)
  })
})
