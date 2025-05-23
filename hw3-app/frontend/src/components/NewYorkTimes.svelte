<script lang="ts">
  import { onMount } from "svelte";
  import "../styles/Homepage.css";
  import CommentSidebar from "./CommentSidebar.svelte";

  let formattedDate = "";
  let articles: any[] = [];
  let API_KEY = "";

  /* Filter out news from the Davis/Sacramento area */
  const FILTER = 'timesTag.location.contains:("Davis","Sacramento")';

  onMount(async () => {
    /* The date function from HW1 */
    const today = new Date();
    const options: Intl.DateTimeFormatOptions = {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    formattedDate = today.toLocaleDateString("en-US", options);

    /* await the API Key and Articles */
    /* await the commentNum and login status */
    await fetchAPIKey();
    await fetchArticles();
    await fetchCommentNum();
    await checkLoginStatus();
  });

  /* fetch function
  fetch the API Key from backend
  */
  async function fetchAPIKey() {
    try {
      const response = await fetch("/api/key");
      const data = await response.json();
      API_KEY = data.apiKey;
    } catch (error) {
      console.error("Failed to fetch API key:", error);
    }
  }
  /* fetch function
  fetch the articles from The New York Time withe FILTER and API key
  */
  async function fetchArticles() {
    const query = "Davis OR Sacramento";
    try {
      const response = await fetch(
        `https://api.nytimes.com/svc/search/v2/articlesearch.json?q=${encodeURIComponent(query)}&api-key=${API_KEY}`
      );

      const data = await response.json();
      articles = data.response.docs;
      await fetchCommentNum();
    } catch (error) {
      console.error("Failed to fetch NYT articles:", error);
    }
  }

  let user: any = null;
  // check if a user session is active
  async function checkLoginStatus() {
    try {
      const res = await fetch("/me"); // Flask route that returns session["user"]
      if (res.ok) {
        user = await res.json();
      }
    } catch (err) {
      console.error("Could not check login session", err);
    }
  }

  let showSidebar = false;
  // toggle the account sidebar
  function toggleSidebar() {
    showSidebar = !showSidebar;
  }
  // generate some Hello message
  function getGreeting(): string {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  }

  let selectedArticle: any = null;
  let showCommentSidebar = false;

  // open the comment panel for a article
  function openCommentSidebar(article: any) {
    selectedArticle = article;
    showCommentSidebar = true;
  }
  // close the comment sidebar
  function closeCommentSidebar() {
    showCommentSidebar = false;
  }

  let commentNum: Record<string,number> = {};
  // fetch the comment number for each articles
  async function fetchCommentNum() {
    for (const article of articles.slice(0,6)) {
      try{
        const res = await fetch(`/comments/${article._id}`);
        const data = await res.json();
        commentNum[article._id] = data.length; 
      } catch (err) {
        console.error(`Failed to fetch comments for ${article._id}`, err);
        commentNum[article._id] = 0;
      }
    }
  }

</script>

<!-- The header from HW1 -->
<header>
  <div class="header-container">
    <div class="date">
      <b>{formattedDate}</b><br />
      Today's Paper
    </div>
    <h1 class="title">
      <img
        src="TheNewYorkTimes.jpg"
        alt="The New York Times"
        class="title-image"
      />
    </h1>
    <div class="auth-button">
      {#if user}
        <button on:click={toggleSidebar}> Account </button>
      {:else}
        <button on:click={() => (window.location.href = "/login")}>
          Login
        </button>
      {/if}
    </div>
  </div>
</header>

<main>
  {#if showSidebar}
    <div
      class="sidebar-overlay"
      role="button"
      tabindex="0"
      on:click={toggleSidebar}
      on:keydown={(e) =>
        (e.key === "Enter" || e.key === " ") && toggleSidebar()}
    ></div>
     <!-- sidebar with user email, hello massage and logout -->
    <aside class="sidebar">
      <div class="sidebar-content">
        <div class="sidebar-header">
          <strong> {user?.email || "User"} </strong>
          <button class="close-btn" on:click={toggleSidebar}>×</button>
        </div>

        <div class="sidebar-HelloMassage">
          <h2>{getGreeting()}!</h2>
        </div>

        <div class="sidebar-footer"> 
          <button class="logout-btn" on:click={() => (window.location.href = "/logout")}>
            Log out
          </button>

        </div>
        
      </div>
    </aside>
  {/if}

  <section class="grid-container">
    <!-- Show the first 6 article in the article array -->
    {#each articles.slice(0, 6) as article (article._id)}
      <article class="article">
        <!-- Shows an image if the article has a multimedia URL -->
        {#if article.multimedia && article.multimedia.length}
          <img
            class="article-image"
            src={"https://www.nytimes.com/" + article.multimedia[0].url}
            alt={article.headline?.main || "News image"}
          />
        {/if}

        <!-- Displays the article's headline or Untitled Article  -->
        <h2>{article.headline?.main || "Untitled Article"}</h2>
        <p class="article-text">
          {article.abstract || article.snippet || "No summary available."}
        </p>

        <!-- display article link -->
        {#if article.web_url}
          <a href={article.web_url} target="_blank" rel="noopener noreferrer"
            >Origin Article</a
          >
        {/if}
        <!-- comment button with count -->
        <button
          class="comment-button"
          on:click={() => openCommentSidebar(article)}
        >
          💬 {commentNum[article._id] ?? 0}
        </button>
      </article>
    {/each}
  </section>

  <!-- comment sidebar only appears when one of this is selected -->
  {#if showCommentSidebar}
    <CommentSidebar
      articleId={selectedArticle._id}
      articleTitle={selectedArticle.headline.main}
      onClose={closeCommentSidebar}
    />
  {/if}

</main>

<footer>
  <div class="footer-container"></div>
</footer>
