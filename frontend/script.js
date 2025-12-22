const API = "http://localhost:8080";

const chat = document.getElementById("chatContainer");

function addMessage(text, type) {
  const msg = document.createElement("div");
  msg.className = `message ${type}`;
  msg.textContent = text;
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
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

  // Assistant bubble
  const botMsg = document.createElement("div");
  botMsg.className = "message assistant";
  botMsg.textContent = "";
  chat.appendChild(botMsg);
  chat.scrollTop = chat.scrollHeight;

  const response = await fetch(`${API}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ collection, question })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    botMsg.textContent += chunk;
    chat.scrollTop = chat.scrollHeight;
  }
}


loadCollections();
