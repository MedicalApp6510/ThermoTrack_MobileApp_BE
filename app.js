import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';

const app = express();
const PORT = process.env.PORT || 3000;
const apiKey = process.env.GOOGLE_CLOUD_VISION_API_KEY; // 请确保将你的API密钥设置在环境变量中

console.log(apiKey);


app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send('Med App server is up and running!');
});

app.post('/process-image', async (req, res) => {
    console.log('Received image URL:', req.body.imageUrl); // 这将显示你从前端收到的imageUrl
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
         const errorBody = await response.json(); // 确保这是解析响应的唯一地方
         console.error('Vision API Error Response:', JSON.stringify(errorBody, null, 2));
         return res.status(400).json({ error: errorBody }); // 发送错误响应并且return结束处理函数
      }

    const jsonResult = await response.json(); // 这里解析成功响应


      // 提取并返回仅数字部分
      const fullTextAnnotation = jsonResult.responses[0]?.fullTextAnnotation?.text;
      const matches = fullTextAnnotation.match(/\d+(\.\d+)?/); // 匹配数字，包括小数点
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
