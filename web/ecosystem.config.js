module.exports = {
  apps : [{
    name: "api-app",
    script: 'api/app.js',
    watch: '.',
    env: {
      "NODE_ENV": "development",
    },
    env_production: {
      "NODE_ENV": "production",
    }
  }],

  deploy : {
    production : {
      user : 'SSH_USERNAME',
      host : 'SSH_HOSTMACHINE',
      ref  : 'origin/master',
      repo : 'GIT_REPOSITORY',
      path : 'DESTINATION_PATH',
      'pre-deploy-local': '',
      'post-deploy' : 'npm install && pm2 reload ecosystem.config.js --env production',
      'pre-setup': ''
    }
  }
};
