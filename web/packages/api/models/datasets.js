const { PythonShell } = require('python-shell');

const makeQsarDataset = function (assay, chemList) {

    return new Promise( (resolve, reject) => {
        const options = {
            scriptPath: '../../../comptox_ai/scripts',
            mode: 'json',
            args: [
                '--assay-abbrev',
                assay,
                '--chem-list',
                chemList
            ]
        };
        
        const pyshell = PythonShell.run('make_qsar.py', options, (err, results) => {
            if (err) {
                console.log("Error:");
                console.log(err);
                reject(err);
            }
            // console.log(results);
            // return eval(results);
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