const API = "http://localhost:5558";

/* ---------- SIGNUP ---------- */
async function signup() {
  const username = document
    .getElementById("signupUsername")
    .value
    .trim();
  const password = document
    .getElementById("signupPassword")
    .value
    .trim();

  if (!username) {
    alert("Username required");
    return;
  }

  if (!password) {
    alert("Password required");
    return;
  }

  const res = await fetch(
    `${API}/auth/signup?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
    { method: "POST" }
  );

  if (res.status === 409) {
    alert("Username already exists");
    return;
  }

  if (!res.ok) {
    alert("Signup failed");
    return;
  }

  const data = await res.json();

  localStorage.setItem("user_id", data.user_id);
  localStorage.setItem("username", data.username);
  console.log("Signed in as:", data.username);
  window.location.href = "login.html";
}

/* ---------- LOGIN ---------- */
async function login() {
  const username = document
    .getElementById("loginUsername")
    .value
    .trim();
  const password = document
    .getElementById("loginPassword")
    .value
    .trim();

  if (!username) {
    alert("Username required");
    return;
  }

  if (!password) {
    alert("Password required");
    return;
  }

  const res = await fetch(
    `${API}/auth/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
    { method: "POST" }
  );

  if (res.status === 404) {
    alert("User not found. Please sign up.");
    return;
  }

  if (res.status === 401) {
    alert("Invalid password.");
    return;
  }

  if (!res.ok) {
    alert("Login failed");
    return;
  }

  const data = await res.json();

  localStorage.setItem("user_id", data.user_id);
  localStorage.setItem("username", data.username);
  console.log("Logged in as:", data.username);

  window.location.href = "home.html";
}
