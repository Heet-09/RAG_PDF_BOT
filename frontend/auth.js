let auth0Client = null;

const AUTH0_DOMAIN = "";
const AUTH0_CLIENT_ID = "";
const AUTH0_AUDIENCE = "https://rag-api"


async function initAuth() {
  auth0Client = await createAuth0Client({
    domain: AUTH0_DOMAIN,
    clientId: AUTH0_CLIENT_ID,
    authorizationParams: {
      audience: AUTH0_AUDIENCE,
      redirect_uri: window.location.origin
    }
  });

  if (window.location.search.includes("code=")) {
    await auth0Client.handleRedirectCallback();
    window.history.replaceState({}, document.title, "/");
  }

  const isAuth = await auth0Client.isAuthenticated();
  if (!isAuth) {
    await login();
  }
}

async function login() {
  await auth0Client.loginWithRedirect();
}

async function logout() {
  await auth0Client.logout({
    logoutParams: { returnTo: window.location.origin }
  });
}

async function getToken() {
  return await auth0Client.getTokenSilently();
}
