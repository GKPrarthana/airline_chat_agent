async function sendMessage() {
  const input = document.getElementById('input');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  const chat = document.getElementById('chat');

  // Allow sending messages with Enter key
  document.getElementById('input').addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent newline
      sendMessage();
    }
  });


  // Show user message
  const userDiv = document.createElement('div');
  userDiv.className = 'bg-green-100 text-green-800 p-3 rounded-xl self-end w-fit max-w-xs ml-auto';
  userDiv.textContent = message;
  chat.appendChild(userDiv);

  // Scroll to bottom
  chat.scrollTop = chat.scrollHeight;

  // Loading response
  const botDiv = document.createElement('div');
  botDiv.className = 'bg-blue-50 text-gray-600 p-3 rounded-xl w-fit max-w-xs';
  botDiv.textContent = 'Typing...';
  chat.appendChild(botDiv);
  chat.scrollTop = chat.scrollHeight;

  // Fetch reply
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: message })
    });

    const data = await res.json();
    botDiv.textContent = data.response;
  } catch (err) {
    botDiv.textContent = 'Oops! Something went wrong.';
  }

  chat.scrollTop = chat.scrollHeight;
}
