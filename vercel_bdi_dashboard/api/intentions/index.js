// ðŸŒŒ Intentions API Endpoint - Vercel Serverless Function
// Handles intention planning results and execution tracking

const cors = require('cors');

const corsOptions = {
  origin: true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

// In-memory storage untuk demo
let intentionData = {
  latest: null,
  history: [],
  active_plans: [],
  stats: {
    total_plans: 0,
    quantum_plans: 0,
    classical_plans: 0,
    total_actions_planned: 0,
    average_quality_score: 0,
    completed_plans: 0
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
        } else if (query.action === 'schedule') {
          return handleGetSchedule(req, res);
        } else if (query.action === 'stats') {
          return handleGetStats(req, res);
        } else if (query.action === 'active') {
          return handleGetActivePlans(req, res);
        } else {
          return handleGetLatest(req, res);
        }

      case 'POST':
        return handlePostIntention(req, res);

      default:
        res.setHeader('Allow', ['GET', 'POST']);
        return res.status(405).json({ 
          error: 'Method not allowed',
          timestamp: new Date().toISOString()
        });
    }
  } catch (error) {
    console.error('Intentions API error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      timestamp: new Date().toISOString()
    });
  }
}

function handleGetLatest(req, res) {
  return res.status(200).json({
    success: true,
    data: intentionData.latest,
    timestamp: new Date().toISOString(),
    message: intentionData.latest ? 'Latest intention plan retrieved' : 'No intention plans available'
  });
}

function handleGetHistory(req, res) {
  const limit = Math.min(parseInt(req.query.limit) || 50, 100);
  const history = intentionData.history.slice(-limit);

  return res.status(200).json({
    success: true,
    data: {
      history: history,
      total_count: intentionData.history.length,
      returned_count: history.length
    },
    timestamp: new Date().toISOString()
  });
}

function handleGetSchedule(req, res) {
  const latest = intentionData.latest;
  const schedule = latest?.plan?.schedule || [];

  // Add execution status
  const enrichedSchedule = schedule.map(item => ({
    ...item,
    status: getActionStatus(item),
    time_until_start: getTimeUntilStart(item.start_time),
    progress_percentage: getProgressPercentage(item)
  }));

  return res.status(200).json({
    success: true,
    data: {
      schedule: enrichedSchedule,
      total_actions: schedule.length,
      plan_id: latest?.id || null,
      planning_type: latest?.planning_type || 'unknown'
    },
    timestamp: new Date().toISOString()
  });
}

function handleGetStats(req, res) {
  return res.status(200).json({
    success: true,
    data: intentionData.stats,
    timestamp: new Date().toISOString()
  });
}

function handleGetActivePlans(req, res) {
  // Filter active plans (not completed and within planning horizon)
  const now = new Date();
  const activePlans = intentionData.active_plans.filter(plan => {
    const completionDate = new Date(plan.plan?.metrics?.completion_date || now);
    return completionDate > now && plan.status !== 'completed';
  });

  return res.status(200).json({
    success: true,
    data: {
      active_plans: activePlans,
      count: activePlans.length
    },
    timestamp: new Date().toISOString()
  });
}

function handlePostIntention(req, res) {
  const intentionPayload = req.body;

  if (!intentionPayload || typeof intentionPayload !== 'object') {
    return res.status(400).json({
      error: 'Invalid intention data format',
      timestamp: new Date().toISOString()
    });
  }

  if (!intentionPayload.timestamp || !intentionPayload.planning_type) {
    return res.status(400).json({
      error: 'Missing required fields: timestamp, planning_type',
      timestamp: new Date().toISOString()
    });
  }

  const processedIntention = {
    ...intentionPayload,
    received_at: new Date().toISOString(),
    id: generateId(),
    status: 'active'
  };

  intentionData.latest = processedIntention;
  intentionData.history.push(processedIntention);
  if (intentionData.history.length > 1000) {
    intentionData.history.shift();
  }
  intentionData.active_plans.push(processedIntention);

  intentionData.stats.total_plans += 1;
  if (processedIntention.planning_type === 'quantum') {
    intentionData.stats.quantum_plans += 1;
  } else {
    intentionData.stats.classical_plans += 1;
  }

  const actionsCount = processedIntention.selected_actions || 0;
  const qualityScore = processedIntention.plan?.quality_metrics?.overall_quality || 0;

  intentionData.stats.total_actions_planned += actionsCount;
  const totalCount = intentionData.stats.total_plans;
  const currentQualityAvg = intentionData.stats.average_quality_score;

  intentionData.stats.average_quality_score = (currentQualityAvg * (totalCount - 1) + qualityScore) / totalCount;

  return res.status(201).json({
    success: true,
    data: {
      id: processedIntention.id,
      received_at: processedIntention.received_at,
      planning_type: processedIntention.planning_type,
      selected_actions: actionsCount,
      quality_score: qualityScore,
      completion_date: processedIntention.plan?.metrics?.completion_date
    },
    message: 'Intention plan stored successfully',
    timestamp: new Date().toISOString()
  });
}

function getActionStatus(action) {
  const now = new Date();
  const startTime = new Date(action.start_time);
  const endTime = new Date(action.end_time);

  if (now < startTime) return 'pending';
  if (now >= startTime && now <= endTime) return 'in_progress';
  return 'completed';
}

function getTimeUntilStart(startTimeStr) {
  const now = new Date();
  const startTime = new Date(startTimeStr);
  const diffMs = startTime.getTime() - now.getTime();
  if (diffMs <= 0) return 0;
  return Math.ceil(diffMs / (1000 * 60 * 60)); // hours
}

function getProgressPercentage(action) {
  const now = new Date();
  const startTime = new Date(action.start_time);
  const endTime = new Date(action.end_time);
  if (now < startTime) return 0;
  if (now >= endTime) return 100;
  const totalDuration = endTime.getTime() - startTime.getTime();
  const elapsed = now.getTime() - startTime.getTime();
  return Math.round((elapsed / totalDuration) * 100);
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
