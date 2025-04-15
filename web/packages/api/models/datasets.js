const { PythonShell } = require('python-shell');

/**
 * 
 * @param {*} assay 
 * @param {*} chemList 
 * @returns 
 */
const makeQsarDataset = function (assay, chemList) {

    let scriptArgs = [
        '--assay-abbrev',
        assay
    ];
    console.log("Testing...");
    if (chemList !== undefined) {
        console.log("No list provided!");
        scriptArgs.push('--chem-list', chemList);
    }

    console.log("Args:");
    console.log(scriptArgs);

    return new Promise( (resolve, reject) => {
        const options = {
            scriptPath: '../../../comptox_ai/scripts',
            mode: 'json',
            args: scriptArgs
        };
        
        const pyshell = PythonShell.run('make_qsar.py', options, (err, results) => {
            if (err) {
                console.log("Error:");
                console.log(err);
                reject(err);
            }
            return (results);
        });

        pyshell.stdout.on('data', function(data) {
            resolve(JSON.parse(data));
        });
        pyshell.end();
    });
}

module.exports = {
    makeQsarDataset: makeQsarDataset,
};