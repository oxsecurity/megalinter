#! /usr/bin/env node
'use strict'
const { MegaLinterRunner } = require('../lib/index')
const assert = require('assert')

const latestRelease = process.env.MEGALINTER_RELEASE || 'insiders'

describe('Module', function () {
    it('(Module) run on own code base', async () => {
        const options = {
            path: './..',
            release: latestRelease,
            debug: true
        }
        await new MegaLinterRunner().run(options)
        assert(process.exitCode === 0, `process.exitCode is 0 (${process.exitCode} returned)`)
    })
})
