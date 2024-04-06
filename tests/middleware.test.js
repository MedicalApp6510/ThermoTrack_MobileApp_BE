// middleware.test.js
const request = require('supertest');
const express = require('express');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());

app.post('/test', (req, res) => {
  res.status(200).json(req.body);
});

test('CORS should allow cross-origin requests', async () => {
  const response = await request(app).post('/test').send({ key: 'value' });
  expect(response.headers['access-control-allow-origin']).toEqual('*');
  expect(response.statusCode).toBe(200);
  expect(response.body).toEqual({ key: 'value' });
});
