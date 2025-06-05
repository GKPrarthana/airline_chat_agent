const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views/index.html'));
});

app.post('/chat', async (req, res) => {
  const userInput = req.body.user_input;

  try {
    const response = await axios.post('http://127.0.0.1:8000/chat', { user_input: userInput });
    res.json(response.data);
  } catch (error) {
    console.error(error.message);
    res.status(500).json({ response: 'Something went wrong.' });
  }
});

app.listen(PORT, () => {
  console.log(`Frontend running at http://localhost:${PORT}`);
});
