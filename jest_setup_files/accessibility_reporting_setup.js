/* global require, expect, beforeAll, afterAll */
const fs = require('fs');
const path = require('path');
const pa11y = require('pa11y');
const puppeteer = require('puppeteer');
const htmlReporter = require('pa11y/lib/reporters/html');

const chromeOptions = {"args": ["--no-sandbox"], "headless": "new"};

const defaultOptions = {
    "runners": ["axe", "htmlcs"],
    "includeWarnings": true,
    "includeNotices": true
}

const reportFolder = "accessibility_reports";

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

function writeReport(report, url, colourScheme) {
    let filename = url.replace(/\/$/, '').split('/').pop();
    if (colourScheme !== undefined) {
        filename = filename + '_' + colourScheme;
    }
    let outputPath = path.join(reportFolder, filename + '.html');
    let i = 1;
    while (fs.existsSync(outputPath)) {
        let new_filename = filename + '_' + i;
        outputPath = path.join(reportFolder, new_filename + '.html');
        i += 1;
    }
    fs.writeFileSync(outputPath, report);
}

expect.extend({
    async toBeAccessible (url, actions, waitTime, colourScheme, newBrowser) {
        const options = defaultOptions;
        if (actions !== undefined) {
            options["actions"] = actions;
        }
        if (waitTime !== undefined) {
            options["wait"] = waitTime;
        }
        const report = await runPa11y(url, options, colourScheme, newBrowser);
        const htmlReport = await htmlReporter.results(report);
        writeReport(htmlReport, url, colourScheme);
        return {
            pass: true
        }
    }
});

expect.extend({
    async allToBeAccessible(urls, colourScheme) {
        let report, htmlReport;
        for (let i = 0; i < urls.length; i += 1) {
            report = await runPa11y(urls[i], defaultOptions, colourScheme);
            htmlReport = await htmlReporter.results(report);
            writeReport(htmlReport, urls[i], colourScheme);
        }
        return {
            pass: true
        }
    
    }
});

expect.extend({
    async toHaveNoErrors(report, filename, colourScheme) {
        const htmlReport = await htmlReporter.results(report);
        writeReport(htmlReport, filename, colourScheme);
        return {
            pass: true
        }
    }
});
