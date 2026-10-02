import crypto from "crypto";
import express from "express";

const app = express();
const port = 3001;
const secret = process.env.WEBHOOK_SECRET || "local_webhook_secret_change_me";

const processedEventIds = new Set();

app.use(express.raw({ type: "application/json", limit: "1mb" }));

function isValidSignature(rawBody, receivedSignature) {
  const expectedSignature = crypto
    .createHmac("sha256", secret)
    .update(rawBody)
    .digest("hex");

  if (!receivedSignature) return false;

  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature, "utf8"),
    Buffer.from(receivedSignature, "utf8")
  );
}

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "webhook-receiver" });
});

app.post("/webhooks/identity", (req, res) => {
  const signature = req.get("X-Webhook-Signature");
  const eventId = req.get("X-Event-Id");

  if (!eventId) {
    return res.status(400).json({ error: "Missing X-Event-Id" });
  }

  if (!isValidSignature(req.body, signature)) {
    return res.status(401).json({ error: "Invalid webhook signature" });
  }

  if (processedEventIds.has(eventId)) {
    console.log(JSON.stringify({
      level: "info",
      message: "duplicate_event_ignored",
      eventId
    }));

    return res.status(200).json({ status: "already_processed", eventId });
  }

  const event = JSON.parse(req.body.toString("utf8"));
  processedEventIds.add(eventId);

  console.log(JSON.stringify({
    level: "info",
    message: "identity_event_received",
    eventId,
    eventType: event.event_type,
    correlationId: event.payload?.correlation_id,
    verificationStatus: event.payload?.status
  }));

  return res.status(202).json({ status: "accepted", eventId });
});

app.listen(port, () => {
  console.log(`Webhook receiver listening on port ${port}`);
});