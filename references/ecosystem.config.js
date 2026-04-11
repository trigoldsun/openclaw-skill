/**
 * PM2 Ecosystem Configuration
 * 
 * This file configures PM2 process manager for production deployments.
 * Place in project root and run: pm2 start ecosystem.config.js --env production
 */

module.exports = {
  apps: [
    {
      name: "my-app", // Change to your app name
      script: "./dist/index.js", // Entry point
      cwd: "/var/www/my-app", // Working directory on server

      // Environment-specific settings
      env: {
        NODE_ENV: "development",
        PORT: 3000,
      },
      env_production: {
        NODE_ENV: "production",
        PORT: 3000,
      },
      env_staging: {
        NODE_ENV: "staging",
        PORT: 3001,
      },

      // Process management
      instances: "auto", // Auto-detect CPU cores and use optimal number
      exec_mode: "cluster", // Use cluster mode for multi-core utilization
      max_memory_restart: "1G", // Restart if memory exceeds limit (increased from 512M)

      // Logging configuration
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      merge_logs: true, // Merge stdout/stderr logs
      error_file: "./logs/err.log",
      out_file: "./logs/out.log",

      // Auto-restart behavior
      autorestart: true,
      watch: false, // Disable watch in production
      ignore_watch: ["node_modules", "logs", "uploads"],
      max_restarts: 10, // Maximum restarts before giving up
      min_uptime: "10s", // Minimum uptime before considering crash

      // Startup options
      spawn_timeout: 3000,
      ready_timeout: 60000,

      // Error handling
      err_handler: {
        handler: "fetch",
        source: "local",
        location: "./logs/error-handler.log",
      },

      // Environment variables from file
      env_variables_lookup: true,
      env_development: {
        DB_HOST: "localhost",
        DB_USER: "dev_user",
      },

      // Optional: Pre/post start scripts
      pre_start: "npm run build",
      post_start: "echo 'App started successfully!'",

      // Graceful shutdown configuration
      kill_timeout: 3000,
      listen_timeout: 10000,

      // Worker specific settings
      workers_exponential_backoff: false,
      force_kill: true,
    },
  ],
};

// Export for different module systems
if (typeof module !== "undefined" && module.exports) {
  module.exports = module.exports;
}
