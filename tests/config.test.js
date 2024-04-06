// config.test.js
require('dotenv').config();

test('PORT environment variable is loaded', () => {
  expect(process.env.PORT).toBeDefined();
});
