// api/status/index.js (Versi Lengkap dan Benar)
const cors = require('cors');
const https = require('https');

const corsOptions = {
  origin: true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

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
        return res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    console.error('Status API error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

function handleGetStatus(req, res) {
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
    }
  });
}

function handleHealthCheck(req, res) {
  return res.status(200).json({ success: true, data: { status: 'healthy' } });
}

function handleGetMetrics(req, res) {
  return res.status(200).json({ success: true, data: systemStatus.metrics });
}

async function handleGitHubStatus(req, res) {
  // Implementasi ini akan kita sederhanakan untuk sekarang
  return res.status(200).json({ success: true, data: { status: 'not_implemented_yet' } });
}

function handleUpdateStatus(req, res) {
  const { component, status, data } = req.body;
  if (component && systemStatus.components[component]) {
    systemStatus.components[component].status = status;
    systemStatus.components[component].last_seen = new Date().toISOString();
    Object.assign(systemStatus.components[component], data);
    systemStatus.last_updated = new Date().toISOString();
    return res.status(200).json({ message: `Status for ${component} updated.` });
  }
  return res.status(400).json({ error: 'Invalid component.' });
}
