<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import "../styles/CommentSidebar.css";
  export let articleId: string;
  export let articleTitle: string;

  let comments: any[] = [];
  let newComment = "";
  const dispatch = createEventDispatcher();

  async function fetchComments() {
    const safeArticleId = encodeURIComponent(articleId);
    const res = await fetch(`/comments/${safeArticleId}`);
    comments = await res.json();
  }

  async function postComment() {
    if (!newComment.trim()) return;
    //Sends a POST Requrest
    const safeArticleId = encodeURIComponent(articleId);

    await fetch(`/comments/${safeArticleId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comment: newComment }),
    });
    newComment = "";
    //reloads comment
    fetchComments();
  }

  onMount(fetchComments);
</script>

<div
  class="sidebar-overlay"
  role="button"
  tabindex="0"
  on:click={() => dispatch("close")}
  on:keydown={(e) => (e.key === "Enter" || e.key === " ") && dispatch("close")}
></div>
<aside class="comment-sidebar">
  <div class="sidebar-content">
    <button class="close-btn" on:click={() => dispatch("close")}>×</button>
    <h3>Comments for:</h3>
    <p><em>{articleTitle}</em></p>

    <div class="comment-list">
      {#each comments as comment}
        <div class="comment-item">
          <strong>{comment.user_name}</strong>
          <p>{comment.comment}</p>
          <small>{new Date(comment.timestamp).toLocaleString()}</small>
        </div>
      {/each}
    </div>

    <div class="comment-form">
      <textarea bind:value={newComment} placeholder="Write a comment..."
      ></textarea>

      <button on:click={postComment}>Post</button>
    </div>
  </div>
</aside>
