nano vercel_bdi_dashboard/api/desires/index.js
```*   **Kode**: (Salin seluruh isi dari **`desires_api_content`** di dokumenmu. Ini adalah kode lengkapnya, kamu tinggal **COPAS**.)
```javascript
// ðŸŒŒ Desires API Endpoint - Vercel Serverless Function  
// Handles desire optimization results and monitoring

const cors = require('cors');

const corsOptions = {
  origin: true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

// In-memory storage untuk demo
let desireData = {
  latest: null,
  history: [],
  stats: {
    total_optimizations: 0,
    qaoa_optimizations: 0,
    classical_optimizations: 0,
    average_net_value: 0,
    total_desires_selected: 0
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
        if (query.action === 'history') {
          return handleGetHistory(req, res);
        } else if (query.action === 'stats') {
          return handleGetStats(req, res);
        } else if (query.action === 'status') {
          return handleGetStatus(req, res);
        } else {
          return handleGetLatest(req, res);
        }
        
      case 'POST':
        return handlePostDesire(req, res);
        
      default:
        res.setHeader('Allow', ['GET', 'POST']);
        return res.status(405).json({ 
          error: 'Method not allowed',
          timestamp: new Date().toISOString()
        });
    }
  } catch (error) {
    console.error('Desires API error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      timestamp: new Date().toISOString()
    });
  }
}

function handleGetLatest(req, res) {
  return res.status(200).json({
    success: true,
    data: desireData.latest,
    timestamp: new Date().toISOString(),
    message: desireData.latest ? 'Latest desire data retrieved' : 'No desire data available'
  });
}

function handleGetHistory(req, res) {
  const limit = Math.min(parseInt(req.query.limit) || 50, 100);
  const history = desireData.history.slice(-limit);
  
  return res.status(200).json({
    success: true,
    data: {
      history: history,
      total_count: desireData.history.length,
      returned_count: history.length
    },
    timestamp: new Date().toISOString()
  });
}

function handleGetStats(req, res) {
  return res.status(200).json({
    success: true,
    data: desireData.stats,
    timestamp: new Date().toISOString()
  });
}

function handleGetStatus(req, res) {
  const latest = desireData.latest;
  
  const status = {
    last_optimization: latest?.timestamp || null,
    optimization_type: latest?.optimization_type || 'unknown',
    selected_desires: latest?.solution?.total_selected || 0,
    optimization_score: latest?.solution?.optimization_score?.net_value || 0,
    is_healthy: latest && (Date.now() - new Date(latest.timestamp).getTime()) < 24 * 60 * 60 * 1000
  };
  
  return res.status(200).json({
    success: true,
    data: status,
    timestamp: new Date().toISOString()
  });
}

function handlePostDesire(req, res) {
  const desirePayload = req.body;
  
  if (!desirePayload || typeof desirePayload !== 'object') {
    return res.status(400).json({
      error: 'Invalid desire data format',
      timestamp: new Date().toISOString()
    });
  }
  
  if (!desirePayload.timestamp || !desirePayload.optimization_type) {
    return res.status(400).json({
      error: 'Missing required fields: timestamp, optimization_type',
      timestamp: new Date().toISOString()
    });
  }
  
  const processedDesire = {
    ...desirePayload,
    received_at: new Date().toISOString(),
    id: generateId()
  };
  
  desireData.latest = processedDesire;
  desireData.history.push(processedDesire);
  if (desireData.history.length > 1000) {
    desireData.history.shift();
  }
  
  desireData.stats.total_optimizations += 1;
  if (processedDesire.optimization_type === 'quantum_qaoa') {
    desireData.stats.qaoa_optimizations += 1;
  } else {
    desireData.stats.classical_optimizations += 1;
  }
  
  const netValue = processedDesire.solution?.optimization_score?.net_value || 0;
  const totalSelected = processedDesire.solution?.total_selected || 0;
  const totalCount = desireData.stats.total_optimizations;
  const currentNetAvg = desireData.stats.average_net_value;
  
  desireData.stats.average_net_value = (currentNetAvg * (totalCount - 1) + netValue) / totalCount;
  desireData.stats.total_desires_selected += totalSelected;
  
  return res.status(201).json({
    success: true,
    data: {
      id: processedDesire.id,
      received_at: processedDesire.received_at,
      optimization_type: processedDesire.optimization_type,
      selected_desires: totalSelected,
      net_value: netValue
    },
    message: 'Desire optimization data stored successfully',
    timestamp: new Date().toISOString()
  });
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
