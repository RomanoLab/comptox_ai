module.exports = {
  apps : [
    {
      name: "api-app",
      script: 'app.js',
      cwd: 'packages/api/',
      watch: true,
      env: {
        "NODE_ENV": "production",
      },
      env_production: {
        "NODE_ENV": "production",
      }
    }
  ]
};
