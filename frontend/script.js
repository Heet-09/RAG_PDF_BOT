const API = "http://localhost:5454";

const chat = document.getElementById("chatContainer");

function addMessage(text, type) {
  const msg = document.createElement("div");
  msg.className = `message ${type}`;
  msg.textContent = text;
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
  return msg;
}

function addTypingIndicator() {
  const msg = document.createElement("div");
  msg.className = "message assistant typing";
  msg.textContent = "...";
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
  return msg;
}

async function uploadPDF() {
  const file = document.getElementById("pdfUpload").files[0];
  if (!file) return;

  addMessage(`Uploading "${file.name}"…`, "assistant");

  const formData = new FormData();
  formData.append("file", file);

  await fetch(`${API}/upload`, {
    method: "POST",
    body: formData
  });

  await loadCollections();
  addMessage("PDF indexed successfully ✅", "assistant");
}

async function loadCollections() {
  const res = await fetch(`${API}/collections`);
  const data = await res.json();

  const select = document.getElementById("pdfSelect");
  select.innerHTML = "";

  for (let key in data) {
    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = data[key];
    select.appendChild(opt);
  }
}

async function askQuestion() {
  const collection = document.getElementById("pdfSelect").value;
  const input = document.getElementById("question");
  const question = input.value.trim();

  if (!question || !collection) return;

  addMessage(question, "user");
  input.value = "";

  // Show typing indicator
  const typingMsg = addTypingIndicator();

  const response = await fetch(`${API}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ collection, question })
  });

  // Replace typing indicator with real assistant message
  typingMsg.innerHTML = "";
  typingMsg.classList.remove("typing");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    typingMsg.textContent += decoder.decode(value);
    chat.scrollTop = chat.scrollHeight;
  }
}


loadCollections();
