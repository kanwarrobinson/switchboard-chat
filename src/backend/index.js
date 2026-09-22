const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(cors());

// ─── MongoDB connection ───────────────────────────────────────────────────────

const mongoUri =
  process.env.MONGO_URI ||
  `mongodb://${process.env.MONGO_USERNAME}:${process.env.MONGO_PASSWORD}` +
  `@${process.env.MONGO_HOST}:${process.env.MONGO_PORT}/${process.env.MONGO_DB}`;

mongoose
  .connect(mongoUri)
  .then(() => console.log('[db] MongoDB connected'))
  .catch((err) => console.error('[db] MongoDB connection error:', err.message));

// ─── Routes ──────────────────────────────────────────────────────────────────

// Health check — used by liveness and readiness probes
app.get('/health', (req, res) => {
  const dbState = mongoose.connection.readyState;
  res.json({
    status: 'ok',
    service: 'backend',
    db: dbState === 1 ? 'connected' : 'disconnected',
    uptime: process.uptime(),
  });
});

// Main API route
app.get('/api', (req, res) => {
  res.json({
    message: 'Backend is running',
    env: process.env.NODE_ENV || 'development',
    db: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
  });
});

// Example: get all items (replace with real business logic)
app.get('/api/items', async (req, res) => {
  try {
    // Placeholder — replace with real model queries
    res.json({ items: [], total: 0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─── Start server ─────────────────────────────────────────────────────────────

app.listen(PORT, () => {
  console.log(`[server] Backend running on port ${PORT}`);
});
