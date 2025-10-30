/* global require */
const fs = require('fs');
const path = require('path');

const reportFolder = 'accessibility_reports';

if (!fs.existsSync(reportFolder)) {
    fs.mkdirSync(reportFolder);
} else {
    fs.readdirSync(reportFolder).forEach(file => fs.rmSync(path.join(reportFolder, file), {recursive:true}));
}

// eslint-disable-next-line no-undef
process.stdout.write('Please review these reports, available in the ' + reportFolder + ' folder, and act on the information provided.\n' + 
                     'The reports give details of which features of the tested page need manual testing ' +
                     'to ensure that they meet the accessibility guidelines.\n'
                    );
