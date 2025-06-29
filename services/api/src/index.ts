import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import * as Sentry from '@sentry/node';
import { config } from './config';
import { errorHandler } from './middleware/errorHandler';
import { authRoutes } from './routes/auth';
import { partnerRoutes } from './routes/partners';
import { campaignRoutes } from './routes/campaigns';
import { analyticsRoutes } from './routes/analytics';

// Initialize Sentry
Sentry.init({
  dsn: config.sentry.dsn,
  environment: config.environment,
});

const app: Application = express();

// Middleware
app.use(Sentry.Handlers.requestHandler());
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/partners', partnerRoutes);
app.use('/api/campaigns', campaignRoutes);
app.use('/api/analytics', analyticsRoutes);

// Error handling
app.use(Sentry.Handlers.errorHandler());
app.use(errorHandler);

const PORT = config.port || 8000;

app.listen(PORT, () => {
  console.log(`🚀 API Server running on port ${PORT}`);
  console.log(`📊 Environment: ${config.environment}`);
});

export default app;