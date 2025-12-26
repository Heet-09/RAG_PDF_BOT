const API = "http://localhost:5555";

const chat = document.getElementById("chatContainer");
const CURRENT_USER_ID = localStorage.getItem("user_id");
const CURRENT_USERNAME = localStorage.getItem("username");
let ACTIVE_CONVERSATION_ID = null;
let ACTIVE_CONVERSATION_PDFS = [];


if (!CURRENT_USER_ID) {
  window.location.href = "login.html";
}

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
    headers: {
      "X-User-Id": CURRENT_USER_ID
    },
    method: "POST",
    body: formData
  });

  await loadCollections();
  addMessage("PDF indexed successfully ✅", "assistant");
}

async function loadCollections() {
  const res = await fetch(`${API}/collections`, {
    headers: {
      "X-User-Id": CURRENT_USER_ID
    }
  });

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
  const select = document.getElementById("pdfSelect");
  const collections =
    ACTIVE_CONVERSATION_ID
      ? ACTIVE_CONVERSATION_PDFS
      : Array.from(select.selectedOptions).map(o => o.value);


  if (collections.length === 0 || collections.length > 3) {
    alert("Please select up to 3 PDFs");
    return;
  }
  const input = document.getElementById("question");
  const question = input.value.trim();

  if (!question) return;


  addMessage(question, "user");
  input.value = "";

  // Show typing indicator
  const typingMsg = addTypingIndicator();

  const response = await fetch(`${API}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Id": CURRENT_USER_ID
    },

    body: JSON.stringify({
      collections: collections,
      question: question,
      conversation_id: ACTIVE_CONVERSATION_ID
    })

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

function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}



const activeUserEl = document.getElementById("activeUser");

if (activeUserEl && CURRENT_USERNAME) {
  activeUserEl.textContent = `Logged in as: ${CURRENT_USERNAME}`;
}


async function loadConversations() {
  const res = await fetch(`${API}/conversations`, {
    headers: { "X-User-Id": CURRENT_USER_ID }
  });

  const data = await res.json();
  const list = document.getElementById("conversationList");

  list.innerHTML = ""; // ✅ clear only chat items

  data.forEach(convo => {
    const item = document.createElement("div");
    item.className = "conversation-item";

    const pdfs = convo.pdf_names;
    item.textContent =
      pdfs[0] + (pdfs.length > 1 ? ` +${pdfs.length - 1}` : "");

    item.onclick = () => openConversation(convo.id);
    list.appendChild(item);
  });
}

async function openConversation(conversationId) {
  ACTIVE_CONVERSATION_ID = conversationId;
  chat.innerHTML = "";

  // Find conversation PDFs
  const convoRes = await fetch(`${API}/conversations`, {
    headers: { "X-User-Id": CURRENT_USER_ID }
  });
  const convos = await convoRes.json();

  const convo = convos.find(c => c.id === conversationId);
  ACTIVE_CONVERSATION_PDFS = convo.pdf_names;

  // Auto-select PDFs in dropdown
  const select = document.getElementById("pdfSelect");
  Array.from(select.options).forEach(opt => {
    opt.selected = ACTIVE_CONVERSATION_PDFS.includes(opt.value);
  });

  const res = await fetch(
    `${API}/conversations/${conversationId}/messages`,
    { headers: { "X-User-Id": CURRENT_USER_ID } }
  );

  const messages = await res.json();
  messages.forEach(msg => addMessage(msg.content, msg.role));
}


loadCollections();
loadConversations();


function startNewChat() {
  ACTIVE_CONVERSATION_ID = null;
  ACTIVE_CONVERSATION_PDFS = [];

  // Clear chat UI
  chat.innerHTML = `
    <div class="message assistant">
      Hi 👋  
      Upload a PDF and start asking questions from it.
    </div>
  `;

  // Clear PDF selections
  const select = document.getElementById("pdfSelect");
  Array.from(select.options).forEach(opt => opt.selected = false);
}
