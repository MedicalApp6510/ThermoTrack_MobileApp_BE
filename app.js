import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Health check
app.get('/', (req, res) => {
  res.send('Med App server is up and running!');
});

// Image processing endpoint
// Request body format: {"imageUrl": "https://example.com/image.jpg"}
app.post('/process-image', (req, res) => {
    // Get the image URL from the request body
    const imageUrl = req.body.imageUrl;
  
    // Spawn a child process to run the Python script
    const pythonProcess = spawn('python', ['./ImgToDigitTool/main.py', imageUrl]);
  
    // Capture script output
    let logs = '';

    pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        logs += output;
    });
  
    // Handle errors
    pythonProcess.stderr.on('data', (data) => {
      console.error(`Error from Python script: ${data}`);
      // Send error response
      res.status(500).send('Error processing image. \nLog: '+ logs);
    });

    // When the script exits
    pythonProcess.on('exit', (code) => {
      // Send response with result and logs
        res.json({ result: getResult(logs), logs: logs });
    });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

// Helper function
function getResult(str) {
    const regex = /Recognized digits: \[([^\]]+)\]/;
    const match = str.match(regex);

    if (match) {
        const result = JSON.parse(`[${match[1].replace(/'/g, '"')}]`);
        return result;
    } else {
        return "";
    }
}