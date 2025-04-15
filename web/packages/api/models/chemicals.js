const { execSync } = require("node:child_process");
const { appendFileSync } = require('fs');
const tmp = require('tmp');
const { parseString } = require('xml2js');
const { access } = require("node:fs");

let parseCmlData = function (cmlData) {
    const molecules = cmlData.cml.molecule.map(m => {
        const mol_props = m.propertyList[0].property.reduce((propObj, item) => {
            let propTitle = item['$'].title;
            let propValue = item.scalar[0];
            return {...propObj, [propTitle]: propValue};
        }, {});
        return mol_props;
    })
    return molecules;
}

const runStructureSearch = function (req) {
    return new Promise(function(resolve, reject) {
        // Save mol file payload as temporary file
        const tmpobj = tmp.fileSync({ postfix: '.mol' });
        appendFileSync(tmpobj.fd, req.body);

        // Call jcsearch using the temp file
        const cml_data_raw = execSync(
            `jcsearch -q ${tmpobj.name} -f cml -t:i DB:public.chemicals`,
            {
                maxBuffer: (1024*1024*24)
            }
        ).toString();

        var cml_obj;
        parseString(cml_data_raw, function (err, result) {
            cml_obj = result;
        });
        
        const mols = parseCmlData(cml_obj);
        resolve(mols);
    });
}

module.exports = {
    runStructureSearch: runStructureSearch
};
