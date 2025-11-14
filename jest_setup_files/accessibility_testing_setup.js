/* global require, expect */
const pa11y = require('pa11y');
const cliReporter = require('pa11y/lib/reporters/cli');
const puppeteer = require('puppeteer');

const chromeOptions = {"args": ["--no-sandbox"], "headless": "new"};

const defaultOptions = {
    "runners": ["axe", "htmlcs"],
}

let browser;

beforeAll(async () => {
    browser = await puppeteer.launch(chromeOptions);
});

afterAll(async () => {
    await browser.close();
});


async function runPa11y(url, options, colourScheme, newBrowser) {
    if (newBrowser) {
        await browser.close();
        browser = await puppeteer.launch(chromeOptions);
    }
    const page = await browser.newPage();
    if (colourScheme !== undefined) {
        await page.emulateMediaFeatures([
            {name: 'prefers-color-scheme', value: colourScheme}
        ]);
    }
    options.browser = browser;
    options.page = page;
    const results = await pa11y(url, options);
    await page.close()
    return results;
}

function checkReport(report) {
    const errors = report.issues;
    const failures = [];
    for (let i = 0; i < errors.length; i += 1) {
        if (errors[i].typeCode === 1) {
            failures.push(errors[i])
        }
    }
    return failures;
}

expect.extend({
    async toBeAccessible (url, actions, waitTime, colourScheme, newBrowser) {
        const options = defaultOptions
        if (actions !== undefined) {
            options["actions"] = actions;
        }
        if (waitTime !== undefined) {
            options["wait"] = waitTime;
        }
        const report = await runPa11y(url, options, colourScheme, newBrowser);
        const result = checkReport(report);
        if (result.length > 0) {
            const results = await cliReporter.results(report)
            return {
                pass: false,
                message: () => results
            }
        } else {
            return {
                pass: true
            }
        }
    }
});

expect.extend({
    async allToBeAccessible(urls, colourScheme) {
        let report;
        let fail = false;
        let results = '';
        const options = defaultOptions;
        for (let i = 0; i < urls.length; i += 1) {
            report = await runPa11y(urls[i], options, colourScheme);
            const result = checkReport(report);
            if (result.length > 0) {
                fail = true;
                results = results.concat(await cliReporter.results(report));
            } 
        }
        if (fail) {
            return {
                pass: false,
                message: () => results
            }
        } else {
            return {
                pass: true
            }
        }
    }
});

expect.extend({
    async toHaveNoErrors(report) {
        const result = checkReport(report);
        if (result.length === 0) {
            return {
                pass: true
            }
        } else {
            const results = await cliReporter.results(report)
            return {
                pass: false,
                message: () => results
            }
        }
    }
});