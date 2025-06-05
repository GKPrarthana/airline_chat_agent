async function sendMessage() {
  const input = document.getElementById('input');
  const message = input.value;
  input.value = '';

  const chat = document.getElementById('chat');

  // Show user message
  const userDiv = document.createElement('div');
  userDiv.className = 'bubble user';
  userDiv.textContent = message;
  chat.appendChild(userDiv);

  // Send to backend
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: message })
  });
  const data = await res.json();

  // Show bot response
  const botDiv = document.createElement('div');
  botDiv.className = 'bubble bot';
  botDiv.textContent = data.response;
  chat.appendChild(botDiv);
}
