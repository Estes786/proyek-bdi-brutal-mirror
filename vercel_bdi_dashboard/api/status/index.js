// ðŸŒŒ Status API Endpoint - System Health and Monitoring
// Provides overall system status and health checks

const cors = require('cors');
const https = require('https');

const corsOptions = {
  origin: true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

// System status tracking
let systemStatus = {
  last_updated: new Date().toISOString(),
  components: {
    termux_agent: { status: 'unknown', last_seen: null },
    github_actions: { status: 'unknown', last_run: null },
    quantum_processor: { status: 'unknown', last_quantum_job: null },
    vercel_dashboard: { status: 'healthy', uptime: 0 }
  },
  metrics: {
    total_cycles: 0,
    successful_cycles: 0,
    failed_cycles: 0,
    quantum_jobs: 0,
    classical_fallbacks: 0,
    average_cycle_time: 0
  }
};

export default async function handler(req, res) {
  await new Promise((resolve) => {
    cors(corsOptions)(req, res, resolve);
  });

  const { method, query } = req;

  try {
    switch (method) {
      case 'GET':
        if (query.action === 'health') {
          return handleHealthCheck(req, res);
        } else if (query.action === 'metrics') {
          return handleGetMetrics(req, res);
        } else if (query.action === 'github') {
          return handleGitHubStatus(req, res);
        } else {
          return handleGetStatus(req, res);
        }

      case 'POST':
        return handleUpdateStatus(req, res);

      default:
        res.setHeader('Allow', ['GET', 'POST']);
        return res.status(405).json({ 
          error: 'Method not allowed',
          timestamp: new Date().toISOString()
        });
    }
  } catch (error) {
    console.error('Status API error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      timestamp: new Date().toISOString()
    });
  }
}

function handleGetStatus(req, res) {
  // Update Vercel dashboard uptime
  const now = new Date();
  systemStatus.components.vercel_dashboard.uptime = now.getTime();
  systemStatus.last_updated = now.toISOString();

  // Calculate overall health
  const componentHealth = Object.values(systemStatus.components).map(comp => {
    if (comp.status === 'healthy' || comp.status === 'active') return 1;
    if (comp.status === 'degraded' || comp.status === 'warning') return 0.5;
    return 0;
  });

  const overallHealth = componentHealth.reduce((a, b) => a + b, 0) / componentHealth.length;

  return res.status(200).json({
    success: true,
    data: {
      ...systemStatus,
      overall_health: overallHealth,
      health_status: overallHealth >= 0.8 ? 'healthy' : overallHealth >= 0.5 ? 'degraded' : 'unhealthy'
    },
    timestamp: new Date().toISOString()
  });
}

function handleHealthCheck(req, res) {
  const healthStatus = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory_usage: process.memoryUsage(),
    version: process.version,
    checks: {
      api_responsive: true,
      database_connected: true, // Mock for demo
      external_apis: true       // Mock for demo
    }
  };

  const allHealthy = Object.values(healthStatus.checks).every(check => check === true);
  if (!allHealthy) {
    healthStatus.status = 'degraded';
  }

  return res.status(200).json({
    success: true,
    data: healthStatus,
    timestamp: new Date().toISOString()
  });
}

function handleGetMetrics(req, res) {
  return res.status(200).json({
    success: true,
    data: systemStatus.metrics,
    timestamp: new Date().toISOString()
  });
}

async function handleGitHubStatus(req, res) {
  const githubRepo = process.env.GITHUB_REPOSITORY || 'user/repo';
  const githubToken = process.env.GITHUB_TOKEN;

  try {
    const workflowData = await fetchGitHubWorkflows(githubRepo, githubToken);

    systemStatus.components.github_actions = {
      status: workflowData.status,
      last_run: workflowData.last_run,
      recent_runs: workflowData.recent_runs
    };

    return res.status(200).json({
      success: true,
      data: workflowData,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    systemStatus.components.github_actions.status = 'error';

    return res.status(200).json({
      success: false,
      error: 'Failed to fetch GitHub status',
      data: { status: 'error', last_run: null },
      timestamp: new Date().toISOString()
    });
  }
}

function handleUpdateStatus(req, res) {
  const statusUpdate = req.body;

  if (!statusUpdate || typeof statusUpdate !== 'object') {
    return res.status(400).json({
      error: 'Invalid status update format',
      timestamp: new Date().toISOString()
    });
  }

  if (statusUpdate.component && statusUpdate.status) {
    if (systemStatus.components[statusUpdate.component]) {
      systemStatus.components[statusUpdate.component].status = statusUpdate.status;
      systemStatus.components[statusUpdate.component].last_seen = new Date().toISOString();

      if (statusUpdate.data) {
        Object.assign(systemStatus.components[statusUpdate.component], statusUpdate.data);
      }
    }
  }

  if (statusUpdate.metrics) {
    Object.assign(systemStatus.metrics, statusUpdate.metrics);
  }

  systemStatus.last_updated = new Date().toISOString();

  return res.status(200).json({
    success: true,
    message: 'Status updated successfully',
    timestamp: new Date().toISOString()
  });
}

async function fetchGitHubWorkflows(repo, token) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.github.com',
      port: 443,
      path: `/repos/${repo}/actions/runs?per_page=5`,
      method: 'GET',
      headers: {
        'User-Agent': 'BDI-Agent-Dashboard',
        'Accept': 'application/vnd.github.v3+json'
      }
    };

    if (token) {
      options.headers['Authorization'] = `token ${token}`;
    }

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const response = JSON.parse(data);

          if (response.workflow_runs && response.workflow_runs.length > 0) {
            const recentRuns = response.workflow_runs.slice(0, 5);
            const lastRun = recentRuns[0];

            const successCount = recentRuns.filter(run => run.conclusion === 'success').length;
            const status = successCount >= recentRuns.length * 0.6 ? 'healthy' : 'degraded';

            resolve({
              status: status,
              last_run: lastRun.created_at,
              recent_runs: recentRuns.map(run => ({
                id: run.id,
                status: run.status,
                conclusion: run.conclusion,
                created_at: run.created_at,
                workflow_name: run.name
              }))
            });
          } else {
            resolve({ status: 'unknown', last_run: null, recent_runs: [] });
          }
        } catch (error) {
          reject(error);
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error('GitHub API request timeout'));
    });

    req.end();
  });
}
