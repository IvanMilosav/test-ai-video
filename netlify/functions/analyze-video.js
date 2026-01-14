// Netlify Background Function for video analysis
// Background functions can run up to 15 minutes (on paid plans)
// Free tier: Still has 10 second timeout - won't work for video analysis
//
// NOTE: This requires Netlify Pro/Business plan for background functions
// Free tier users should use Railway for backend

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const writeFile = promisify(fs.writeFile);
const unlink = promisify(fs.unlink);

exports.handler = async (event, context) => {
  // Background function - appends '-background' to function name
  const isBackground = context.functionName.endsWith('-background');

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    // Parse multipart form data
    const contentType = event.headers['content-type'] || '';

    if (!contentType.includes('multipart/form-data')) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          error: 'Netlify serverless functions have strict limitations:',
          details: [
            '- 10 second timeout on free tier',
            '- 26 second timeout on Pro tier',
            '- Background functions: 15 min on Pro/Business (not available on free)',
            '- Video analysis typically takes 5-15 minutes',
            '',
            'RECOMMENDATION: Use Railway for backend API',
            'Railway supports long-running processes and is free for small projects'
          ]
        })
      };
    }

    // For background functions, return immediately with job ID
    if (isBackground) {
      // Start analysis in background
      // This would need a queue system like AWS SQS, Redis, or database
      return {
        statusCode: 202,
        body: JSON.stringify({
          message: 'Analysis started',
          jobId: 'mock-job-id',
          note: 'Check status at /api/status/{jobId}'
        })
      };
    }

    // Regular function - will timeout
    return {
      statusCode: 503,
      body: JSON.stringify({
        error: 'Video analysis not available on Netlify free tier',
        solution: 'Deploy backend to Railway: https://railway.app',
        reason: 'Netlify function timeout (10s free, 26s Pro) too short for video analysis (5-15 min)'
      })
    };

  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
