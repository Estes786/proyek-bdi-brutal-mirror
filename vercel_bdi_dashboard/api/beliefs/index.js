// ðŸŒŒ Beliefs API Endpoint - Vercel Serverless Function
// Handles belief data submission and retrieval

const cors = require('cors');

// CORS configuration
const corsOptions = {
  origin: true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

// In-memory storage untuk demo (production should use database)
let beliefData = {
  latest: null,
  history: [],
  stats: {
    total_processed: 0,
    quantum_processed: 0,
    classical_processed: 0,
    average_optimization_score: 0
  }
};

export default async function handler(req, res) {
  // Handle CORS
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
        } else {
          return handleGetLatest(req, res);
        }

      case 'POST':
        return handlePostBelief(req, res);

      default:
        res.setHeader('Allow', ['GET', 'POST']);
        return res.status(405).json({ 
          error: 'Method not allowed',
          timestamp: new Date().toISOString()
        });
    }
  } catch (error) {
    console.error('Beliefs API error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      timestamp: new Date().toISOString()
    });
  }
}

function handleGetLatest(req, res) {
  return res.status(200).json({
    success: true,
    data: beliefData.latest,
    timestamp: new Date().toISOString(),
    message: beliefData.latest ? 'Latest belief data retrieved' : 'No belief data available'
  });
}

function handleGetHistory(req, res) {
  const limit = Math.min(parseInt(req.query.limit) || 50, 100);
  const history = beliefData.history.slice(-limit);

  return res.status(200).json({
    success: true,
    data: {
      history: history,
      total_count: beliefData.history.length,
      returned_count: history.length
    },
    timestamp: new Date().toISOString()
  });
}

function handleGetStats(req, res) {
  return res.status(200).json({
    success: true,
    data: beliefData.stats,
    timestamp: new Date().toISOString()
  });
}

function handlePostBelief(req, res) {
  const beliefPayload = req.body;

  if (!beliefPayload || typeof beliefPayload !== 'object') {
    return res.status(400).json({
      error: 'Invalid belief data format',
      timestamp: new Date().toISOString()
    });
  }

  // Validate required fields
  if (!beliefPayload.timestamp || !beliefPayload.processing_type) {
    return res.status(400).json({
      error: 'Missing required fields: timestamp, processing_type',
      timestamp: new Date().toISOString()
    });
  }

  // Process and store belief data
  const processedBelief = {
    ...beliefPayload,
    received_at: new Date().toISOString(),
    id: generateId()
  };

  // Update latest
  beliefData.latest = processedBelief;

  // Add to history (keep last 1000 records)
  beliefData.history.push(processedBelief);
  if (beliefData.history.length > 1000) {
    beliefData.history = beliefData.history.slice(-1000);
  }

  // Update stats
  beliefData.stats.total_processed += 1;
  if (processedBelief.processing_type === 'quantum') {
    beliefData.stats.quantum_processed += 1;
  } else {
    beliefData.stats.classical_processed += 1;
  }

  // Update average optimization score
  if (processedBelief.optimized_beliefs?.optimization_score) {
    const currentAvg = beliefData.stats.average_optimization_score;
    const newScore = processedBelief.optimized_beliefs.optimization_score;
    const totalCount = beliefData.stats.total_processed;

    beliefData.stats.average_optimization_score = 
      (currentAvg * (totalCount - 1) + newScore) / totalCount;
  }

  return res.status(201).json({
    success: true,
    data: {
      id: processedBelief.id,
      received_at: processedBelief.received_at,
      processing_type: processedBelief.processing_type,
      total_beliefs: processedBelief.optimized_beliefs?.total_beliefs || 0
    },
    message: 'Belief data stored successfully',
    timestamp: new Date().toISOString()
  });
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
