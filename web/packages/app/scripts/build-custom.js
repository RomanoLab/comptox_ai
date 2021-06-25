// from https://github.com/facebook/create-react-app/issues/5306#issuecomment-447948123
// and https://github.com/greenelab/connectivity-search-frontend/blob/master/scripts/build-non-split.js

const rewire = require('rewire');
const defaults = rewire('react-scripts/scripts/build.js');
const config = defaults.__get__('config');

// Consolidate chunk files into a single main.js
config.optimization.splitChunks = {
  cacheGroups: {
    default: false
  }
};
// Put runtime into bundle
config.optimization.runtimeChunk = false;

// Configure JS output
config.output.filename = 'static/js/main.js';
// Configure CSS output
config.plugins[5].options.filename = 'static/css/main.css';
config.plugins[5].options.moduleFilename = () => 'static/css/main.css';