const express = require('express');
const cors = require('cors');
const { trace, context, propagation } = require('@opentelemetry/api');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { ExpressInstrumentation } = require('@opentelemetry/instrumentation-express');
const { HttpInstrumentation } = require('@opentelemetry/instrumentation-http');
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// --- OTel Setup ---
const provider = new NodeTracerProvider({
    resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: 'mock-api',
    }),
});

const exporter = new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://otel-collector:4318/v1/traces',
});

provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();

registerInstrumentations({
    instrumentations: [
        new HttpInstrumentation(),
        new ExpressInstrumentation(),
    ],
});

const tracer = trace.get_tracer('mock-api-tracer');

// --- Express App ---
const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/quote', (req, res) => {
    const userId = req.query.user_id || 'guest';
    const span = trace.getSpan(context.active());

    const quoteId = `Q-${Math.floor(1000 + Math.random() * 9000)}`;
    const premium = Math.floor(50 + Math.random() * 450);

    if (span) {
        span.setAttribute('user.id', userId);
        span.setAttribute('quote.id', quoteId);
    }

    const traceId = span ? span.spanContext().traceId : '00000000000000000000000000000000';

    res.json({
        quote_id: quoteId,
        premium: premium,
        trace_id: traceId
    });
});

app.post('/api/purchase', (req, res) => {
    const { quote_id, user_id } = req.body;
    const span = trace.getSpan(context.active());

    if (span) {
        span.setAttribute('quote.id', quote_id);
        span.setAttribute('user.id', user_id);
    }

    const traceId = span ? span.spanContext().traceId : '00000000000000000000000000000000';

    res.json({
        status: 'success',
        policy_id: `P-${Math.floor(100000 + Math.random() * 900000)}`,
        trace_id: traceId
    });
});

const PORT = 8080;
app.listen(PORT, () => {
    console.log(`Mock API listening on port ${PORT}`);
});
