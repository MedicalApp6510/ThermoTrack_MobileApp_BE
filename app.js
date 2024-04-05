import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';

const app = express();
const PORT = process.env.PORT || 3000;
const apiKey = process.env.GOOGLE_CLOUD_VISION_API_KEY;

console.log(apiKey);


app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send('Med App server is up and running!');
});

app.post('/process-image', async (req, res) => {
  const imageUrl = req.body.imageUrl;
  const url = `https://vision.googleapis.com/v1/images:annotate?key=${apiKey}`;
  const requestBody = {
      requests: [
          {
              image: {
                  source: { imageUri: imageUrl }
              },
              features: [{ type: "TEXT_DETECTION"}]
          }
      ]
  };

  console.log("Sending request to Vision API with body:", JSON.stringify(requestBody, null, 2));


  try {
      const response = await fetch(url, {
          method: 'POST',
          body: JSON.stringify(requestBody),
          headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
         const errorBody = await response.json();
         console.error('Vision API Error Response:', JSON.stringify(errorBody, null, 2));
         return res.status(400).json({ error: errorBody });
      }

    const jsonResult = await response.json();



      const fullTextAnnotation = jsonResult.responses[0]?.fullTextAnnotation?.text;
      const matches = fullTextAnnotation.match(/\d+(\.\d+)?/);
      const numberText = matches ? matches[0] : 'No numbers found.';

      res.json({ number: numberText });

  } catch (error) {
      console.error('Error calling the Vision API:', error);
      res.status(500).send(`Error processing image: ${error.message}`);
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
